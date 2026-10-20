"""Core domain tables migration

Revision ID: 002_core_domain_tables
Revises: 001_initial_users
Create Date: 2026-10-20 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_core_domain_tables"
down_revision: Union[str, None] = "001_initial_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Categories
    op.create_table(
        "categories",
        sa.Column("category_id", sa.String(length=50), nullable=False),
        sa.Column("category_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("category_id"),
    )
    op.create_index(op.f("ix_categories_category_id"), "categories", ["category_id"], unique=False)

    # 2. Suppliers
    op.create_table(
        "suppliers",
        sa.Column("supplier_id", sa.String(length=50), nullable=False),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("supplier_type", sa.String(length=100), nullable=False, server_default="Wholesaler"),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("lead_time_mean_days", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("lead_time_sd_days", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("on_time_probability", sa.Float(), nullable=False, server_default="0.90"),
        sa.Column("full_fill_probability", sa.Float(), nullable=False, server_default="0.95"),
        sa.Column("payment_terms_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("supplier_id"),
    )
    op.create_index(op.f("ix_suppliers_supplier_id"), "suppliers", ["supplier_id"], unique=False)

    # 3. Medicines
    op.create_table(
        "medicines",
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("generic_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("active_ingredients", sa.String(length=255), nullable=True),
        sa.Column("strength", sa.String(length=100), nullable=False),
        sa.Column("dosage_form", sa.String(length=100), nullable=False),
        sa.Column("route", sa.String(length=50), nullable=False, server_default="Oral"),
        sa.Column("category_id", sa.String(length=50), nullable=False),
        sa.Column("primary_supplier_id", sa.String(length=50), nullable=False),
        sa.Column("unit_of_measure", sa.String(length=50), nullable=False, server_default="strip"),
        sa.Column("pack_size", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("storage_condition", sa.String(length=100), nullable=False, server_default="Room Temperature"),
        sa.Column("unit_cost_inr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("unit_price_inr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("composition_status", sa.String(length=100), nullable=False, server_default="VERIFIED_STANDARD_REFERENCE"),
        sa.Column("composition_note", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["category_id"], ["categories.category_id"]),
        sa.ForeignKeyConstraint(["primary_supplier_id"], ["suppliers.supplier_id"]),
        sa.PrimaryKeyConstraint("medicine_id"),
    )
    op.create_index(op.f("ix_medicines_medicine_id"), "medicines", ["medicine_id"], unique=False)
    op.create_index(op.f("ix_medicines_category_id"), "medicines", ["category_id"], unique=False)
    op.create_index(op.f("ix_medicines_primary_supplier_id"), "medicines", ["primary_supplier_id"], unique=False)

    # 4. Inventory Current
    op.create_table(
        "inventory_current",
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("opening_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("closing_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_received_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_sold_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_adjusted_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wastage_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_ordered_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("on_order_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_point", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("order_up_to_level", sa.Integer(), nullable=False, server_default="500"),
        sa.Column("days_of_cover", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("stock_status", sa.String(length=50), nullable=False, server_default="IN_STOCK"),
        sa.Column("safety_stock", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("moq", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("expected_daily_demand", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.medicine_id"]),
        sa.PrimaryKeyConstraint("medicine_id"),
    )
    op.create_index(op.f("ix_inventory_current_medicine_id"), "inventory_current", ["medicine_id"], unique=False)

    # 5. Transactions
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("transaction_date", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_inr", sa.Float(), nullable=True),
        sa.Column("total_value_inr", sa.Float(), nullable=True),
        sa.Column("stock_before", sa.Integer(), nullable=False),
        sa.Column("stock_after", sa.Integer(), nullable=False),
        sa.Column("reference_number", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=False, server_default="System"),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.medicine_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_id"), "transactions", ["id"], unique=False)
    op.create_index(op.f("ix_transactions_medicine_id"), "transactions", ["medicine_id"], unique=False)
    op.create_index(op.f("ix_transactions_transaction_date"), "transactions", ["transaction_date"], unique=False)

    # 6. Daily Records
    op.create_table(
        "daily_records",
        sa.Column("record_id", sa.String(length=50), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("category_id", sa.String(length=50), nullable=False),
        sa.Column("supplier_id", sa.String(length=50), nullable=False),
        sa.Column("closing_stock", sa.Integer(), nullable=False),
        sa.Column("on_order_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_point", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("units_demanded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("units_sold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sales_7d_avg", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("sales_30d_avg", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("days_of_cover", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("stock_position_cover_days", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("days_since_last_receipt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stockout_days_last_30d", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("supplier_lead_time_mean_days", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("supplier_full_fill_probability", sa.Float(), nullable=False, server_default="0.95"),
        sa.Column("supplier_disruption_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("unit_price_inr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("stockout_today", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("stockout_next_7d", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.medicine_id"]),
        sa.PrimaryKeyConstraint("record_id"),
    )
    op.create_index("ix_daily_records_med_date", "daily_records", ["medicine_id", "date"], unique=True)
    op.create_index(op.f("ix_daily_records_record_id"), "daily_records", ["record_id"], unique=False)

    # 7. ML Runs & Forecasts
    op.create_table(
        "ml_runs",
        sa.Column("run_id", sa.String(length=50), nullable=False),
        sa.Column("run_date", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("mae", sa.Float(), nullable=False),
        sa.Column("rmse", sa.Float(), nullable=False),
        sa.Column("wape", sa.Float(), nullable=False),
        sa.Column("parameters_json", sa.Text(), nullable=True),
        sa.Column("selection_reason", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("run_id"),
    )

    op.create_table(
        "forecasts",
        sa.Column("forecast_id", sa.String(length=50), nullable=False),
        sa.Column("run_id", sa.String(length=50), nullable=True),
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False, server_default="Gradient Boosting Regressor"),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("predicted_demand", sa.Float(), nullable=False),
        sa.Column("lower_bound", sa.Float(), nullable=False),
        sa.Column("upper_bound", sa.Float(), nullable=False),
        sa.Column("is_forecast", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.medicine_id"]),
        sa.ForeignKeyConstraint(["run_id"], ["ml_runs.run_id"]),
        sa.PrimaryKeyConstraint("forecast_id"),
    )
    op.create_index(op.f("ix_forecasts_medicine_id"), "forecasts", ["medicine_id"], unique=False)
    op.create_index(op.f("ix_forecasts_forecast_date"), "forecasts", ["forecast_date"], unique=False)

    # 8. Risk Results
    op.create_table(
        "risk_results",
        sa.Column("risk_id", sa.String(length=50), nullable=False),
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("calculated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(length=50), nullable=False, server_default="LOW"),
        sa.Column("expected_daily_demand", sa.Float(), nullable=False),
        sa.Column("stock_coverage_days", sa.Float(), nullable=False),
        sa.Column("lead_time_days", sa.Float(), nullable=False),
        sa.Column("safety_stock", sa.Integer(), nullable=False),
        sa.Column("required_stock", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("factors_json", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.medicine_id"]),
        sa.PrimaryKeyConstraint("risk_id"),
    )
    op.create_index(op.f("ix_risk_results_medicine_id"), "risk_results", ["medicine_id"], unique=False)

    # 9. Replenishment Recommendations
    op.create_table(
        "replenishment_recommendations",
        sa.Column("recommendation_id", sa.String(length=50), nullable=False),
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("supplier_id", sa.String(length=50), nullable=False),
        sa.Column("current_stock", sa.Integer(), nullable=False),
        sa.Column("open_order_qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("required_stock", sa.Integer(), nullable=False),
        sa.Column("lead_time_days", sa.Float(), nullable=False),
        sa.Column("moq_applied", sa.Integer(), nullable=False),
        sa.Column("recommended_order_quantity", sa.Integer(), nullable=False),
        sa.Column("is_urgent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("ordered_at", sa.DateTime(), nullable=True),
        sa.Column("dismissed_at", sa.DateTime(), nullable=True),
        sa.Column("accepted_by", sa.String(length=100), nullable=True),
        sa.Column("dismissed_by", sa.String(length=100), nullable=True),
        sa.Column("dismiss_reason", sa.Text(), nullable=True),
        sa.Column("po_reference", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.medicine_id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.supplier_id"]),
        sa.PrimaryKeyConstraint("recommendation_id"),
    )
    op.create_index(op.f("ix_replenishment_recommendations_medicine_id"), "replenishment_recommendations", ["medicine_id"], unique=False)

    # 10. Alerts
    op.create_table(
        "alerts",
        sa.Column("alert_id", sa.String(length=50), nullable=False),
        sa.Column("medicine_id", sa.String(length=50), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="UNREAD"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("acknowledged_by", sa.String(length=100), nullable=True),
        sa.Column("resolved_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.medicine_id"]),
        sa.PrimaryKeyConstraint("alert_id"),
    )
    op.create_index(op.f("ix_alerts_medicine_id"), "alerts", ["medicine_id"], unique=False)

    # 11. App Settings & Dataset Imports
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "dataset_imports",
        sa.Column("import_id", sa.String(length=50), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=True),
        sa.Column("row_count", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="SUCCESS"),
        sa.Column("imported_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("import_id"),
    )

    # 12. Audit Log
    op.create_table(
        "audit_log",
        sa.Column("log_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("log_id"),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("dataset_imports")
    op.drop_table("app_settings")
    op.drop_table("alerts")
    op.drop_table("replenishment_recommendations")
    op.drop_table("risk_results")
    op.drop_table("forecasts")
    op.drop_table("ml_runs")
    op.drop_table("daily_records")
    op.drop_table("transactions")
    op.drop_table("inventory_current")
    op.drop_table("medicines")
    op.drop_table("suppliers")
    op.drop_table("categories")
