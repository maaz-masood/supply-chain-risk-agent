from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), unique=True)
    buyer_id = Column(String(50))
    supplier_id = Column(String(50))
    product_category = Column(String(100))
    quantity_ordered = Column(Integer)
    order_date = Column(Date)
    dispatch_date = Column(Date)
    delivery_date = Column(Date)
    shipping_mode = Column(String(50))
    order_value_usd = Column(Float)
    delay_days = Column(Integer)
    disruption_type = Column(String(100))
    disruption_severity = Column(String(50))
    historical_disruption_count = Column(Integer)
    supplier_reliability_score = Column(Float)
    supply_risk = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskReport(Base):
    __tablename__ = "risk_reports"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    suppliers_analyzed = Column(Integer)
    critical_alerts = Column(Integer)
    generated_at = Column(DateTime, default=datetime.utcnow)
    sent_via_email = Column(Boolean, default=False)
    stored_in_drive = Column(Boolean, default=False)