from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models import Order, RiskReport

router = APIRouter()

@router.get("/suppliers/risk")
def get_high_risk_suppliers(db: Session = Depends(get_db)):
    """Get suppliers with highest risk scores"""
    results = db.query(
        Order.supplier_id,
        Order.product_category,
        func.avg(Order.supplier_reliability_score).label("avg_reliability"),
        func.avg(Order.supply_risk).label("avg_risk"),
        func.count(Order.id).label("total_orders"),
        func.sum(Order.delay_days).label("total_delays")
    ).group_by(
        Order.supplier_id,
        Order.product_category
    ).order_by(
        func.avg(Order.supply_risk).desc()
    ).limit(10).all()

    return [
        {
            "supplier_id": r.supplier_id,
            "product_category": r.product_category,
            "avg_reliability_score": round(r.avg_reliability, 2),
            "avg_risk_score": round(r.avg_risk, 2),
            "total_orders": r.total_orders,
            "total_delay_days": r.total_delays
        }
        for r in results
    ]

@router.get("/orders/delayed")
def get_delayed_orders(db: Session = Depends(get_db)):
    """Get orders with significant delays"""
    orders = db.query(Order).filter(
        Order.delay_days > 5
    ).order_by(
        Order.delay_days.desc()
    ).limit(20).all()

    return [
        {
            "order_id": o.order_id,
            "supplier_id": o.supplier_id,
            "product_category": o.product_category,
            "delay_days": o.delay_days,
            "disruption_type": o.disruption_type,
            "disruption_severity": o.disruption_severity,
            "order_value_usd": o.order_value_usd
        }
        for o in orders
    ]

@router.get("/orders/disruptions")
def get_disruptions(db: Session = Depends(get_db)):
    """Get disruption summary by type"""
    results = db.query(
        Order.disruption_type,
        Order.disruption_severity,
        func.count(Order.id).label("count"),
        func.avg(Order.delay_days).label("avg_delay")
    ).group_by(
        Order.disruption_type,
        Order.disruption_severity
    ).order_by(
        func.count(Order.id).desc()
    ).all()

    return [
        {
            "disruption_type": r.disruption_type,
            "severity": r.disruption_severity,
            "count": r.count,
            "avg_delay_days": round(r.avg_delay, 1)
        }
        for r in results
    ]

@router.get("/suppliers/summary")
def get_supplier_summary(db: Session = Depends(get_db)):
    """Get overall supplier performance summary"""
    total_orders = db.query(func.count(Order.id)).scalar()
    avg_delay = db.query(func.avg(Order.delay_days)).scalar()
    high_risk = db.query(func.count(Order.id)).filter(
        Order.supply_risk > 0.5
    ).scalar()
    total_value = db.query(
        func.sum(Order.order_value_usd)
    ).scalar()

    return {
        "total_orders": total_orders,
        "average_delay_days": round(avg_delay, 1),
        "high_risk_orders": high_risk,
        "total_order_value_usd": round(total_value, 2)
    }

@router.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    """Get all generated risk reports"""
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