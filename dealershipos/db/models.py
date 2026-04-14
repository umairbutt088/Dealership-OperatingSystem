import uuid
from datetime import date as DateType, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def new_stock_id() -> str:
    return f"STK-{uuid.uuid4().hex[:10].upper()}"


class Vehicle(Base):
    """Unified stock + sold rows; `stock_id` is the canonical key (not registration)."""

    __tablename__ = "vehicles"

    stock_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    plate: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    plate_norm: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    model: Mapped[Optional[str]] = mapped_column(String(255))
    month: Mapped[Optional[str]] = mapped_column(String(32))  # first-of-month ISO date string
    date_acquired: Mapped[Optional[DateType]] = mapped_column(Date)
    source: Mapped[Optional[str]] = mapped_column(String(128))
    investor: Mapped[Optional[str]] = mapped_column(String(128))
    px_value: Mapped[Optional[float]] = mapped_column(Float)
    purchase_price: Mapped[Optional[float]] = mapped_column(Float)
    recon_cost: Mapped[Optional[float]] = mapped_column(Float)
    total_cost: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[Optional[str]] = mapped_column(String(64))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    days_in_stock: Mapped[Optional[int]] = mapped_column(Integer)

    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    date_sold: Mapped[Optional[DateType]] = mapped_column(Date)
    sold_price: Mapped[Optional[float]] = mapped_column(Float)
    profit: Mapped[Optional[float]] = mapped_column(Float)
    part_ex: Mapped[Optional[float]] = mapped_column(Float)
    sa_investor_profit_share: Mapped[Optional[float]] = mapped_column(Float)
    investor_profit: Mapped[Optional[float]] = mapped_column(Float)
    sa_profit: Mapped[Optional[float]] = mapped_column(Float)
    date_listed: Mapped[Optional[DateType]] = mapped_column(Date)
    platform: Mapped[Optional[str]] = mapped_column(String(128))
    invoice_number: Mapped[Optional[str]] = mapped_column(String(64))
    customer_name: Mapped[Optional[str]] = mapped_column(String(255))
    contact_info: Mapped[Optional[str]] = mapped_column(String(255))
    warranty: Mapped[Optional[str]] = mapped_column(String(128))
    autoguard: Mapped[Optional[str]] = mapped_column(String(128))

    website_listed: Mapped[Optional[bool]] = mapped_column(Boolean)
    at_listed: Mapped[Optional[bool]] = mapped_column(Boolean)
    left_to_do: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Investor(Base):
    __tablename__ = "investors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    initial_balance: Mapped[Optional[float]] = mapped_column(Float)
    capital_returned: Mapped[Optional[float]] = mapped_column(Float)
    total_balance: Mapped[Optional[float]] = mapped_column(Float)
    purchased: Mapped[Optional[float]] = mapped_column(Float)
    total_profit: Mapped[Optional[float]] = mapped_column(Float)
    available: Mapped[Optional[float]] = mapped_column(Float)


class DeliveryRow(Base):
    """Outbound deliveries — persisted (replaces prototype localStorage)."""

    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plate: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    plate_norm: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    model: Mapped[Optional[str]] = mapped_column(String(255))
    addr: Mapped[Optional[str]] = mapped_column(String(512))
    date: Mapped[Optional[DateType]] = mapped_column(Date)
    scheduled_date: Mapped[Optional[DateType]] = mapped_column(Date)
    driver: Mapped[Optional[str]] = mapped_column(String(255))
    cost: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[Optional[str]] = mapped_column(String(64))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    stock_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("vehicles.stock_id"), nullable=True)


class CollectionRow(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[Optional[str]] = mapped_column(String(128))
    date_won: Mapped[Optional[DateType]] = mapped_column(Date)
    plate: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    plate_norm: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    model: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    post_code: Mapped[Optional[str]] = mapped_column(String(32))
    how_far: Mapped[Optional[str]] = mapped_column(String(255))
    collection_date: Mapped[Optional[str]] = mapped_column(String(64))
    number: Mapped[Optional[str]] = mapped_column(String(64))
    additional_notes: Mapped[Optional[str]] = mapped_column(Text)
    stock_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("vehicles.stock_id"), nullable=True)


class ExpenseRow(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[Optional[DateType]] = mapped_column(Date)
    date: Mapped[Optional[DateType]] = mapped_column(Date)
    category: Mapped[Optional[str]] = mapped_column(String(128))
    from_vendor: Mapped[Optional[str]] = mapped_column("vendor_from", String(255))
    amount: Mapped[Optional[float]] = mapped_column(Float)
    payment_method: Mapped[Optional[str]] = mapped_column(String(64))
    paid_by: Mapped[Optional[str]] = mapped_column(String(128))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    reg: Mapped[Optional[str]] = mapped_column(String(64))
    stock_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("vehicles.stock_id"), nullable=True)


class MoneyInRow(Base):
    __tablename__ = "money_in"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[Optional[DateType]] = mapped_column(Date)
    date: Mapped[Optional[DateType]] = mapped_column(Date)
    category: Mapped[Optional[str]] = mapped_column(String(128))
    amount: Mapped[Optional[float]] = mapped_column(Float)
    reg: Mapped[Optional[str]] = mapped_column(String(64))
    plate_norm: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    stock_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("vehicles.stock_id"), nullable=True)


class MoneyOutRow(Base):
    __tablename__ = "money_out"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[Optional[DateType]] = mapped_column(Date)
    date: Mapped[Optional[DateType]] = mapped_column(Date)
    category: Mapped[Optional[str]] = mapped_column(String(128))
    amount: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class CashSpendingRow(Base):
    __tablename__ = "cash_spending"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[Optional[DateType]] = mapped_column(Date)
    amount: Mapped[Optional[float]] = mapped_column(Float)
    cost_incurred_on: Mapped[Optional[str]] = mapped_column(String(255))
    reason: Mapped[Optional[str]] = mapped_column(Text)


class FuelExpenseRow(Base):
    __tablename__ = "fuel_expense"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[Optional[DateType]] = mapped_column(Date)
    date: Mapped[Optional[DateType]] = mapped_column(Date)
    car: Mapped[Optional[str]] = mapped_column(String(255))
    amount: Mapped[Optional[float]] = mapped_column(Float)
    column1: Mapped[Optional[str]] = mapped_column(String(255))


class SorRow(Base):
    __tablename__ = "sor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[Optional[DateType]] = mapped_column(Date)
    date_acquired: Mapped[Optional[DateType]] = mapped_column(Date)
    plate: Mapped[Optional[str]] = mapped_column(String(32))
    plate_norm: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    model: Mapped[Optional[str]] = mapped_column(String(255))
    seller_name: Mapped[Optional[str]] = mapped_column(String(255))
    total_cost: Mapped[Optional[float]] = mapped_column(Float)
    sale_price: Mapped[Optional[float]] = mapped_column(Float)
    breakdown: Mapped[Optional[str]] = mapped_column(Text)
    stock_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("vehicles.stock_id"), nullable=True)


class InvestorCarExpenseRow(Base):
    __tablename__ = "investor_car_expense"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[Optional[DateType]] = mapped_column(Date)
    date: Mapped[Optional[DateType]] = mapped_column(Date)
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    amount: Mapped[Optional[float]] = mapped_column(Float)
    reg: Mapped[Optional[str]] = mapped_column(String(255))
    stock_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("vehicles.stock_id"), nullable=True)


class MonthlySummary(Base):
    """Front Sheet — monthly rollups."""

    __tablename__ = "monthly_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[DateType] = mapped_column(Date, unique=True)
    cars_sold: Mapped[Optional[int]] = mapped_column(Integer)
    total_revenue: Mapped[Optional[float]] = mapped_column(Float)
    total_gross_profit: Mapped[Optional[float]] = mapped_column(Float)
    company_expenses: Mapped[Optional[float]] = mapped_column(Float)
    total_sa_gross_profit: Mapped[Optional[float]] = mapped_column(Float)
    investor_net_profit: Mapped[Optional[str]] = mapped_column(String(128))
    investor_expense: Mapped[Optional[float]] = mapped_column(Float)
    company_fuel_costs: Mapped[Optional[float]] = mapped_column(Float)
    other_money_in: Mapped[Optional[float]] = mapped_column(Float)
    other_money_out: Mapped[Optional[float]] = mapped_column(Float)
    net_profit_exc_investor: Mapped[Optional[float]] = mapped_column(Float)
    net_exc_investor: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class VehicleLineItem(Base):
    """Per-vehicle workbook tabs (cost lines) stored as JSON-friendly rows."""

    __tablename__ = "vehicle_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[str] = mapped_column(String(32), ForeignKey("vehicles.stock_id"), index=True)
    sheet_name: Mapped[Optional[str]] = mapped_column(String(255))
    item_label: Mapped[Optional[str]] = mapped_column(String(255))
    amount: Mapped[Optional[float]] = mapped_column(Float)
    extra: Mapped[Optional[str]] = mapped_column(Text)  # JSON for misc columns
