"""Logical to physical column mappings and data dictionary definitions."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class ColumnDef(BaseModel):
    name: str
    dtype: str
    required: bool = True
    description: str = ""
    is_key: bool = False


# Expected column schemas for each CSV file in the dataset pack
FILE_SCHEMAS: Dict[str, List[ColumnDef]] = {
    "categories.csv": [
        ColumnDef(name="category_id", dtype="str", is_key=True, description="PK, CATnn"),
        ColumnDef(name="category_name", dtype="str", description="Therapeutic category name"),
        ColumnDef(name="description", dtype="str", description="Category therapeutic description"),
    ],
    "suppliers.csv": [
        ColumnDef(name="supplier_id", dtype="str", is_key=True, description="PK, SUPnn"),
        ColumnDef(name="supplier_name", dtype="str", description="Supplier commercial name"),
        ColumnDef(name="supplier_type", dtype="str", description="Supplier channel type"),
        ColumnDef(name="city", dtype="str", description="City location"),
        ColumnDef(name="state", dtype="str", description="State location"),
        ColumnDef(name="lead_time_mean_days", dtype="float", description="Mean order lead time (days)"),
        ColumnDef(name="lead_time_sd_days", dtype="float", description="Std dev of lead time"),
        ColumnDef(name="on_time_probability", dtype="float", description="P(no extra delay)"),
        ColumnDef(name="full_fill_probability", dtype="float", description="P(order delivered in full)"),
        ColumnDef(name="payment_terms_days", dtype="int", description="Payment terms in days"),
        ColumnDef(name="is_synthetic", dtype="int", required=False, description="1 if synthetic entity"),
    ],
    "medicines.csv": [
        ColumnDef(name="medicine_id", dtype="str", is_key=True, description="PK, MEDnnn"),
        ColumnDef(name="generic_name", dtype="str", description="Generic INN name"),
        ColumnDef(name="display_name", dtype="str", description="Brand/display name"),
        ColumnDef(name="active_ingredients", dtype="str", description="Active substances"),
        ColumnDef(name="strength", dtype="str", description="Strength label"),
        ColumnDef(name="dosage_form", dtype="str", description="Dosage form"),
        ColumnDef(name="route", dtype="str", description="Administration route"),
        ColumnDef(name="category_id", dtype="str", description="FK categories"),
        ColumnDef(name="primary_supplier_id", dtype="str", description="FK suppliers"),
        ColumnDef(name="unit_of_measure", dtype="str", description="Smallest stock-keeping unit"),
        ColumnDef(name="pack_size", dtype="int", description="Units per order pack"),
        ColumnDef(name="storage_condition", dtype="str", description="Storage requirement"),
        ColumnDef(name="unit_cost_inr_2021", dtype="float", description="Unit cost in INR"),
        ColumnDef(name="unit_price_inr_2021", dtype="float", description="Unit retail price in INR"),
        ColumnDef(name="composition_status", dtype="str", description="VERIFIED_STANDARD_REFERENCE or UNVERIFIED_REQUIRES_REVIEW"),
        ColumnDef(name="composition_note", dtype="str", required=False, description="Clinical verification note"),
        ColumnDef(name="price_is_synthetic", dtype="int", required=False, description="1 if synthetic price"),
    ],
    "medicine_suppliers.csv": [
        ColumnDef(name="medicine_id", dtype="str", is_key=True, description="FK medicines"),
        ColumnDef(name="supplier_id", dtype="str", is_key=True, description="FK suppliers"),
        ColumnDef(name="supplier_role", dtype="str", description="Primary or Secondary"),
        ColumnDef(name="order_share", dtype="float", description="Approximate share of orders"),
    ],
    "calendar.csv": [
        ColumnDef(name="date", dtype="date", is_key=True, description="Calendar date"),
        ColumnDef(name="year", dtype="int", description="Year"),
        ColumnDef(name="month", dtype="int", description="Month"),
        ColumnDef(name="day_of_week", dtype="int", description="0=Mon..6=Sun"),
        ColumnDef(name="is_weekend", dtype="int", description="1 if Sat/Sun"),
        ColumnDef(name="season", dtype="str", description="Season classification"),
    ],
    "inventory_daily.csv": [
        ColumnDef(name="record_id", dtype="str", is_key=True, description="PK, RECnnnnnn"),
        ColumnDef(name="date", dtype="date", description="Date"),
        ColumnDef(name="medicine_id", dtype="str", description="FK medicines"),
        ColumnDef(name="opening_stock", dtype="int", description="Start of day stock"),
        ColumnDef(name="units_received", dtype="int", description="Units delivered"),
        ColumnDef(name="units_sold", dtype="int", description="Units dispensed"),
        ColumnDef(name="wastage_units", dtype="int", description="Damaged or expired units"),
        ColumnDef(name="closing_stock", dtype="int", description="End of day stock"),
        ColumnDef(name="units_ordered_today", dtype="int", description="Order quantity placed today"),
        ColumnDef(name="on_order_units", dtype="int", description="Outstanding undelivered units"),
        ColumnDef(name="reorder_point", dtype="int", description="Policy reorder point"),
        ColumnDef(name="order_up_to_level", dtype="int", description="Policy order up to level"),
    ],
    "demand_sales_daily.csv": [
        ColumnDef(name="record_id", dtype="str", is_key=True, description="PK, RECnnnnnn"),
        ColumnDef(name="date", dtype="date", description="Date"),
        ColumnDef(name="medicine_id", dtype="str", description="FK medicines"),
        ColumnDef(name="units_demanded", dtype="int", description="Underlying customer demand"),
        ColumnDef(name="units_sold", dtype="int", description="Dispensed units"),
        ColumnDef(name="lost_sales_units", dtype="int", description="Unmet demand due to stock-out"),
        ColumnDef(name="stockout_flag", dtype="int", description="1 if lost_sales_units > 0"),
        ColumnDef(name="unit_price_inr", dtype="float", description="Unit selling price"),
        ColumnDef(name="sales_revenue_inr", dtype="float", description="Total sales revenue"),
    ],
    "replenishment_orders.csv": [
        ColumnDef(name="order_id", dtype="str", is_key=True, description="PK, POnnnnnnn"),
        ColumnDef(name="medicine_id", dtype="str", description="FK medicines"),
        ColumnDef(name="supplier_id", dtype="str", description="FK suppliers"),
        ColumnDef(name="order_date", dtype="date", description="Order placed date"),
        ColumnDef(name="expected_delivery_date", dtype="date", description="Expected delivery date"),
        ColumnDef(name="actual_delivery_date", dtype="date", required=False, description="Actual delivery date"),
        ColumnDef(name="lead_time_days", dtype="float", required=False, description="Actual lead time in days"),
        ColumnDef(name="quantity_ordered", dtype="int", description="Units ordered"),
        ColumnDef(name="quantity_received", dtype="int", required=False, description="Units received"),
        ColumnDef(name="status", dtype="str", description="Received, Partially_Received, In_Transit_At_Period_End"),
        ColumnDef(name="unit_cost_inr", dtype="float", description="Unit cost"),
        ColumnDef(name="order_value_inr", dtype="float", description="Total order value"),
    ],
    "supplier_disruption_events.csv": [
        ColumnDef(name="event_id", dtype="str", is_key=True, description="PK event"),
        ColumnDef(name="supplier_id", dtype="str", description="FK suppliers"),
        ColumnDef(name="start_date", dtype="date", description="Disruption start"),
        ColumnDef(name="end_date", dtype="date", description="Disruption end"),
        ColumnDef(name="extra_lead_time_days", dtype="float", description="Added lead time"),
        ColumnDef(name="full_fill_probability_multiplier", dtype="float", description="Multiplier on full fill"),
    ],
    "stockout_prediction_dataset.csv": [
        ColumnDef(name="record_id", dtype="str", is_key=True, description="PK/FK, RECnnnnnn"),
        ColumnDef(name="date", dtype="date", description="Date"),
        ColumnDef(name="medicine_id", dtype="str", description="FK medicines"),
        ColumnDef(name="category_id", dtype="str", description="FK categories"),
        ColumnDef(name="supplier_id", dtype="str", description="FK suppliers"),
        ColumnDef(name="year", dtype="int", description="Calendar year"),
        ColumnDef(name="month", dtype="int", description="Calendar month"),
        ColumnDef(name="day_of_week", dtype="int", description="0=Mon"),
        ColumnDef(name="is_weekend", dtype="int", description="1 if weekend"),
        ColumnDef(name="season", dtype="str", description="North India seasonal classification"),
        ColumnDef(name="closing_stock", dtype="int", description="End of day stock"),
        ColumnDef(name="on_order_units", dtype="int", description="Outstanding ordered units"),
        ColumnDef(name="reorder_point", dtype="int", description="Policy reorder point"),
        ColumnDef(name="units_demanded", dtype="int", description="Customer demand on day t"),
        ColumnDef(name="units_sold", dtype="int", description="Dispensed units on day t"),
        ColumnDef(name="sales_7d_avg", dtype="float", description="Trailing 7-day average sales"),
        ColumnDef(name="sales_30d_avg", dtype="float", description="Trailing 30-day average sales"),
        ColumnDef(name="days_of_cover", dtype="float", description="closing_stock / sales_30d_avg"),
        ColumnDef(name="stock_position_cover_days", dtype="float", description="(closing + on_order) / sales_30d_avg"),
        ColumnDef(name="days_since_last_receipt", dtype="int", description="Days since last delivery"),
        ColumnDef(name="stockout_days_last_30d", dtype="int", description="Stockout days in past 30d"),
        ColumnDef(name="supplier_lead_time_mean_days", dtype="float", description="Supplier lead time mean"),
        ColumnDef(name="supplier_full_fill_probability", dtype="float", description="Supplier full fill prob"),
        ColumnDef(name="supplier_disruption_active", dtype="int", description="1 if active disruption"),
        ColumnDef(name="unit_price_inr", dtype="float", description="Unit price INR"),
        ColumnDef(name="stockout_today", dtype="int", description="Day t stockout flag"),
        ColumnDef(name="stockout_next_7d", dtype="int", description="TARGET: 1 if stockout occurs in days t+1..t+7"),
    ],
}

# Physical to Logical mapping for field names where CSV column name differs slightly from model field name
MEDICINE_FIELD_MAP = {
    "unit_cost_inr_2021": "unit_cost_inr",
    "unit_price_inr_2021": "unit_price_inr",
}
