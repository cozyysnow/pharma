import uuid
import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from backend.app.db.models.transaction import Transaction, TransactionType
from backend.app.db.models.inventory import InventoryCurrent
from backend.app.db.models.medicine import Medicine
from backend.app.schemas.transaction import TransactionCreate, TransactionSummary
from backend.app.core.errors import InsufficientStockException, NotFoundException, ValidationException


class TransactionService:
    @staticmethod
    def create_transaction(
        db: Session,
        tx_in: TransactionCreate,
        user_name: str = "Authorized Staff",
    ) -> Transaction:
        if tx_in.quantity <= 0:
            raise ValidationException("Transaction quantity must be greater than zero.")

        # Row lock inventory_current to prevent race conditions
        inv = (
            db.query(InventoryCurrent)
            .filter(InventoryCurrent.medicine_id == tx_in.medicine_id)
            .with_for_update()
            .first()
        )
        if not inv:
            raise NotFoundException("Inventory record for medicine", tx_in.medicine_id)

        med = db.query(Medicine).filter(Medicine.medicine_id == tx_in.medicine_id).first()
        unit_price = med.unit_price_inr if med else 0.0

        stock_before = inv.closing_stock
        stock_delta = 0

        # Apply domain rules based on transaction type
        if tx_in.transaction_type == TransactionType.SALE:
            stock_delta = -tx_in.quantity
            inv.units_sold_today += tx_in.quantity

        elif tx_in.transaction_type == TransactionType.RECEIPT:
            stock_delta = tx_in.quantity
            inv.units_received_today += tx_in.quantity
            # Per Sec 9.2: Purchase receipt reduces open orders
            inv.on_order_units = max(0, inv.on_order_units - tx_in.quantity)

        elif tx_in.transaction_type == TransactionType.RETURN_FROM_PATIENT:
            stock_delta = tx_in.quantity

        elif tx_in.transaction_type == TransactionType.TRANSFER_OUT:
            stock_delta = -tx_in.quantity

        elif tx_in.transaction_type == TransactionType.ADJUSTMENT_POSITIVE:
            stock_delta = tx_in.quantity
            inv.units_adjusted_today += tx_in.quantity

        elif tx_in.transaction_type == TransactionType.ADJUSTMENT_NEGATIVE:
            stock_delta = -tx_in.quantity
            inv.units_adjusted_today -= tx_in.quantity

        elif tx_in.transaction_type == TransactionType.WASTAGE:
            stock_delta = -tx_in.quantity
            inv.wastage_units += tx_in.quantity

        stock_after = stock_before + stock_delta

        # Safety Check: Enforce strictly non-negative stock constraint
        if stock_after < 0:
            raise InsufficientStockException(
                medicine_id=tx_in.medicine_id,
                current_stock=stock_before,
                requested_qty=tx_in.quantity,
            )

        # Update physical closing stock
        inv.closing_stock = stock_after

        # Recompute coverage and stock status
        edd = max(0.1, inv.expected_daily_demand)
        inv.days_of_cover = round(inv.closing_stock / edd, 2)
        if inv.closing_stock <= 0:
            inv.stock_status = "OUT_OF_STOCK"
        elif inv.closing_stock <= inv.reorder_point:
            inv.stock_status = "LOW_STOCK"
        elif inv.closing_stock > inv.order_up_to_level:
            inv.stock_status = "OVERSTOCKED"
        else:
            inv.stock_status = "IN_STOCK"

        # Create immutable transaction record
        tx = Transaction(
            id=f"TX_{uuid.uuid4().hex[:10].upper()}",
            transaction_date=datetime.datetime.utcnow(),
            medicine_id=tx_in.medicine_id,
            transaction_type=tx_in.transaction_type,
            quantity=tx_in.quantity,
            unit_price_inr=unit_price,
            total_value_inr=round(tx_in.quantity * unit_price, 2),
            stock_before=stock_before,
            stock_after=stock_after,
            reference_number=tx_in.reference_number,
            notes=tx_in.notes,
            created_by=user_name,
        )
        db.add(tx)

        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def void_transaction(
        db: Session,
        transaction_id: str,
        user_name: str = "Authorized Staff",
        reason: Optional[str] = None,
    ) -> Transaction:
        orig = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not orig:
            raise NotFoundException("Transaction", transaction_id)
        if orig.notes and "[VOIDED" in orig.notes:
            raise ValidationException("Transaction has already been voided.")

        inv = (
            db.query(InventoryCurrent)
            .filter(InventoryCurrent.medicine_id == orig.medicine_id)
            .with_for_update()
            .first()
        )
        if not inv:
            raise NotFoundException("Inventory record for medicine", orig.medicine_id)

        inflow_types = [
            TransactionType.RECEIPT,
            TransactionType.RETURN_FROM_PATIENT,
            TransactionType.ADJUSTMENT_POSITIVE,
        ]
        if orig.transaction_type in inflow_types:
            delta = -orig.quantity
            rev_type = TransactionType.ADJUSTMENT_NEGATIVE
        else:
            delta = orig.quantity
            rev_type = TransactionType.ADJUSTMENT_POSITIVE

        stock_before = inv.closing_stock
        stock_after = stock_before + delta
        if stock_after < 0:
            raise InsufficientStockException(
                medicine_id=orig.medicine_id,
                current_stock=stock_before,
                requested_qty=orig.quantity,
            )

        inv.closing_stock = stock_after
        edd = max(0.1, inv.expected_daily_demand)
        inv.days_of_cover = round(inv.closing_stock / edd, 2)
        if inv.closing_stock <= 0:
            inv.stock_status = "OUT_OF_STOCK"
        elif inv.closing_stock <= inv.reorder_point:
            inv.stock_status = "LOW_STOCK"
        elif inv.closing_stock > inv.order_up_to_level:
            inv.stock_status = "OVERSTOCKED"
        else:
            inv.stock_status = "IN_STOCK"

        orig.notes = f"{orig.notes or ''} [VOIDED: {reason or 'Administrative void'}]".strip()

        rev_tx = Transaction(
            id=f"TX_VOID_{uuid.uuid4().hex[:8].upper()}",
            transaction_date=datetime.datetime.utcnow(),
            medicine_id=orig.medicine_id,
            transaction_type=rev_type,
            quantity=orig.quantity,
            unit_price_inr=orig.unit_price_inr,
            total_value_inr=orig.total_value_inr,
            stock_before=stock_before,
            stock_after=stock_after,
            reference_number=f"VOID-{orig.id}",
            notes=f"Compensating transaction for void of {orig.id}. Reason: {reason or 'Administrative void'}",
            created_by=user_name,
        )
        db.add(rev_tx)
        db.commit()
        db.refresh(rev_tx)
        return rev_tx

    @staticmethod
    def list_transactions(
        db: Session,
        medicine_id: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[Transaction], int]:
        q = db.query(Transaction).join(Medicine).options(
            joinedload(Transaction.medicine).joinedload(Medicine.category),
            joinedload(Transaction.medicine).joinedload(Medicine.primary_supplier),
        )

        if medicine_id:
            q = q.filter(Transaction.medicine_id == medicine_id)

        if transaction_type:
            q = q.filter(Transaction.transaction_type == transaction_type)

        if search:
            search_fmt = f"%{search.lower()}%"
            q = q.filter(
                (Medicine.display_name.ilike(search_fmt))
                | (Transaction.reference_number.ilike(search_fmt))
                | (Transaction.id.ilike(search_fmt))
            )

        total = q.count()
        skip = (page - 1) * page_size
        items = q.order_by(Transaction.transaction_date.desc()).offset(skip).limit(page_size).all()
        return items, total

    @staticmethod
    def get_summary(db: Session) -> TransactionSummary:
        txs = db.query(Transaction).all()
        total_count = len(txs)
        inflow = 0
        outflow = 0
        sales_val = 0.0

        for t in txs:
            if t.transaction_type in [TransactionType.RECEIPT, TransactionType.RETURN_FROM_PATIENT, TransactionType.ADJUSTMENT_POSITIVE]:
                inflow += t.quantity
            else:
                outflow += t.quantity
                if t.transaction_type == TransactionType.SALE and t.total_value_inr:
                    sales_val += t.total_value_inr

        return TransactionSummary(
            total_transactions=total_count,
            total_units_inflow=inflow,
            total_units_outflow=outflow,
            total_sales_value_inr=round(sales_val, 2),
        )
