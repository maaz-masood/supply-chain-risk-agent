from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    order_status = Column(String(50))
    shipping_mode = Column(String(50))
    days_shipping_real = Column(Integer)
    days_shipping_scheduled = Column(Integer)
    delivery_status = Column(String(100))
    late_delivery_risk = Column(Integer)
    market = Column(String(50))
    order_region = Column(String(100))
    order_country = Column(String(100))
    category_name = Column(String(100))
    department_name = Column(String(100))
    customer_segment = Column(String(50))
    customer_country = Column(String(100))
    product_name = Column(String(200))
    product_price = Column(Float)
    sales = Column(Float)
    order_profit_per_order = Column(Float)
    benefit_per_order = Column(Float)
    order_item_quantity = Column(Integer)
    order_date = Column(String(50))
    shipping_date = Column(String(50))
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
