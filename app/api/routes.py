from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models import Order, RiskReport

router = APIRouter()

@router.get("/suppliers/risk")
def get_high_risk_suppliers(db: Session = Depends(get_db)):
    results = db.query(
        Order.category_name,
        Order.market,
        Order.order_region,
        func.count(Order.id).label("total_orders"),
        func.sum(Order.late_delivery_risk).label("total_late_risk"),
        func.avg(Order.order_profit_per_order).label("avg_profit"),
        func.avg(Order.days_shipping_real - 
                 Order.days_shipping_scheduled).label("avg_delay")
    ).group_by(
        Order.category_name,
        Order.market,
        Order.order_region
    ).order_by(
        func.sum(Order.late_delivery_risk).desc()
    ).limit(10).all()

    return [
        {
            "category": r.category_name,
            "market": r.market,
            "region": r.order_region,
            "total_orders": r.total_orders,
            "total_late_risk": r.total_late_risk,
            "avg_profit": round(r.avg_profit or 0, 2),
            "avg_delay_days": round(r.avg_delay or 0, 1)
        }
        for r in results
    ]

@router.get("/orders/delayed")
def get_delayed_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).filter(
        Order.days_shipping_real > Order.days_shipping_scheduled
    ).order_by(
        (Order.days_shipping_real - Order.days_shipping_scheduled).desc()
    ).limit(20).all()

    return [
        {
            "order_id": o.order_id,
            "category": o.category_name,
            "market": o.market,
            "shipping_mode": o.shipping_mode,
            "days_real": o.days_shipping_real,
            "days_scheduled": o.days_shipping_scheduled,
            "delay_days": o.days_shipping_real - o.days_shipping_scheduled,
            "delivery_status": o.delivery_status,
            "late_delivery_risk": o.late_delivery_risk,
            "profit": o.order_profit_per_order
        }
        for o in orders
    ]

@router.get("/orders/disruptions")
def get_disruptions(db: Session = Depends(get_db)):
    results = db.query(
        Order.delivery_status,
        Order.shipping_mode,
        func.count(Order.id).label("count"),
        func.avg(Order.days_shipping_real -
                 Order.days_shipping_scheduled).label("avg_delay")
    ).group_by(
        Order.delivery_status,
        Order.shipping_mode
    ).order_by(
        func.count(Order.id).desc()
    ).all()

    return [
        {
            "delivery_status": r.delivery_status,
            "shipping_mode": r.shipping_mode,
            "count": r.count,
            "avg_delay_days": round(r.avg_delay or 0, 1)
        }
        for r in results
    ]

@router.get("/suppliers/summary")
def get_supplier_summary(db: Session = Depends(get_db)):
    total_orders = db.query(func.count(Order.id)).scalar()
    avg_delay = db.query(
        func.avg(Order.days_shipping_real - Order.days_shipping_scheduled)
    ).scalar()
    high_risk = db.query(func.count(Order.id)).filter(
        Order.late_delivery_risk == 1
    ).scalar()
    total_sales = db.query(func.sum(Order.sales)).scalar()
    total_profit = db.query(func.sum(Order.order_profit_per_order)).scalar()

    return {
        "total_orders": total_orders,
        "average_delay_days": round(avg_delay or 0, 1),
        "high_risk_orders": high_risk,
        "total_sales_usd": round(total_sales or 0, 2),
        "total_profit_usd": round(total_profit or 0, 2)
    }

@router.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(RiskReport).order_by(
        RiskReport.generated_at.desc()
    ).limit(10).all()

    return [
        {
            "id": r.id,
            "title": r.title,
            "suppliers_analyzed": r.suppliers_analyzed,
            "critical_alerts": r.critical_alerts,
            "generated_at": r.generated_at,
            "sent_via_email": r.sent_via_email
        }
        for r in reports
    ]