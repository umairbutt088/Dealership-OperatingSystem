"""Build `APP_DATA`-shaped payloads for the legacy frontend."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from dealershipos.db.models import (
    CollectionRow,
    DeliveryRow,
    ExpenseRow,
    Investor,
    MoneyInRow,
    MoneyOutRow,
    MonthlySummary,
    Vehicle,
)


def _d(d: date | None) -> str | None:
    if d is None:
        return None
    return d.isoformat()


def vehicle_to_stock_dict(v: Vehicle) -> dict[str, Any]:
    return {
        "stock_id": v.stock_id,
        "plate": v.plate,
        "model": v.model or "",
        "month": v.month or "",
        "date_acquired": _d(v.date_acquired) or "",
        "source": v.source or "",
        "investor": v.investor or "",
        "purchase_price": v.purchase_price or 0,
        "recon_cost": v.recon_cost or 0,
        "total_cost": v.total_cost or 0,
        "status": v.status or "",
        "notes": v.notes or "",
        "days_in_stock": v.days_in_stock or 0,
        "left_to_do": v.left_to_do or "",
        "website_listed": bool(v.website_listed) if v.website_listed is not None else False,
        "autotrader_listed": bool(v.at_listed) if v.at_listed is not None else False,
        "todo": [],
    }


def vehicle_to_sold_dict(v: Vehicle) -> dict[str, Any]:
    return {
        "stock_id": v.stock_id,
        "plate": v.plate,
        "model": v.model or "",
        "month": v.month or "",
        "date_acquired": _d(v.date_acquired) or "",
        "date_sold": _d(v.date_sold) or "",
        "days_in_stock": v.days_in_stock or 0,
        "total_cost": v.total_cost or 0,
        "sold_price": v.sold_price or 0,
        "profit": v.profit or 0,
        "investor": v.investor or "",
        "platform": v.platform or "",
        "customer_name": v.customer_name or "",
        "contact_info": v.contact_info or "",
        "warranty": v.warranty or "",
        "invoice_number": v.invoice_number or "",
        "autoguard": v.autoguard or "",
        "status": v.status or "Sold",
    }


def build_app_state(db: Session) -> dict[str, Any]:
    stock_vehicles = list(db.scalars(select(Vehicle).where(Vehicle.is_sold.is_(False))))
    sold_vehicles = list(db.scalars(select(Vehicle).where(Vehicle.is_sold.is_(True))))
    investors = list(db.scalars(select(Investor)))

    monthly_rows = list(db.scalars(select(MonthlySummary).order_by(MonthlySummary.month)))
    monthly: list[dict[str, Any]] = []
    if not monthly_rows:
        monthly = [
            {
                "month": "",
                "label": "—",
                "cars_sold": 0,
                "revenue": 0.0,
                "gross_profit": 0.0,
                "net_profit": 0.0,
            }
        ]
    else:
        for m in monthly_rows:
            label = m.month.strftime("%b %Y") if m.month else ""
            monthly.append(
                {
                    "month": m.month.isoformat() if m.month else "",
                    "label": label,
                    "cars_sold": m.cars_sold or 0,
                    "revenue": float(m.total_revenue or 0),
                    "gross_profit": float(m.total_gross_profit or 0),
                    "net_profit": float(m.net_exc_investor or m.net_profit_exc_investor or 0),
                }
            )

    expenses = list(db.scalars(select(ExpenseRow)))
    expense_out = [
        {
            "month": _d(e.month) if e.month else "",
            "date": _d(e.date) if e.date else "",
            "category": e.category or "",
            "from": e.from_vendor or "",
            "amount": e.amount or 0,
            "payment_method": e.payment_method or "",
            "paid_by": e.paid_by or "",
            "notes": e.notes or "",
        }
        for e in expenses
    ]

    cols = list(db.scalars(select(CollectionRow)))
    collections_out: list[dict[str, Any]] = []
    for c in cols:
        dw = _d(c.date_won) if c.date_won else ""
        collections_out.append(
            {
                "id": f"col{c.id}",
                "source": c.source or "",
                "date_won": dw,
                "plate": c.plate or "",
                "model": c.model or "",
                "addr": c.location or "",
                "post_code": c.post_code or "",
                "how_far": c.how_far or "",
                "collection_date": c.collection_date or "",
                "number": c.number or "",
                "notes": c.additional_notes or "",
                "type": "Incoming",
                "status": "Pending",
                "driver": "",
                "cost": 0,
                "days_pending": 0,
                "distance_note": c.how_far or "",
                "linked_vehicles": [],
            }
        )

    money_in = list(db.scalars(select(MoneyInRow)))
    money_in_out = [
        {
            "month": _d(mi.month) if mi.month else "",
            "date": _d(mi.date) if mi.date else "",
            "category": mi.category or "",
            "amount": mi.amount or 0,
            "plate": mi.reg or "",
            "notes": mi.notes or "",
        }
        for mi in money_in
    ]

    money_out = list(db.scalars(select(MoneyOutRow)))
    money_out_out = [
        {
            "month": _d(mo.month) if mo.month else "",
            "date": _d(mo.date) if mo.date else "",
            "category": mo.category or "",
            "amount": mo.amount or 0,
            "notes": mo.notes or "",
        }
        for mo in money_out
    ]

    dels = list(db.scalars(select(DeliveryRow)))
    deliveries_out: list[dict[str, Any]] = []
    for d in dels:
        dw = _d(d.date) if d.date else ""
        deliveries_out.append(
            {
                "id": f"d{d.id}",
                "type": "Delivery",
                "plate": d.plate or "",
                "model": d.model or "",
                "addr": d.addr or "",
                "date": dw,
                "scheduled_date": _d(d.scheduled_date) if d.scheduled_date else dw,
                "driver": d.driver or "",
                "cost": d.cost or 0,
                "status": d.status or "Pending",
                "notes": d.notes or "",
                "days_pending": 0,
                "distance_note": "",
                "linked_vehicles": [],
            }
        )

    return {
        "sold": [vehicle_to_sold_dict(v) for v in sold_vehicles],
        "stock": [vehicle_to_stock_dict(v) for v in stock_vehicles],
        "investors": [
            {
                "name": i.name,
                "initial_balance": i.initial_balance or 0,
                "capital_returned": i.capital_returned or 0,
                "total_balance": i.total_balance or 0,
                "purchased": i.purchased or 0,
                "total_profit": i.total_profit or 0,
                "available": i.available or 0,
            }
            for i in investors
        ],
        "monthly": monthly,
        "expenses": expense_out,
        "collections": collections_out,
        "deliveries": deliveries_out,
        "money_in": money_in_out,
        "money_out": money_out_out,
    }
