import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.connection import SessionLocal, create_tables
from app.database.models import Order

def load_csv_data(filepath: str, limit: int = 50000):
    create_tables()
    db = SessionLocal()
    count = 0

    df = pd.read_csv(filepath, encoding='latin-1', nrows=limit)
    print(f"Loading {len(df)} records...")

    for _, row in df.iterrows():
        order = Order(
            order_id=int(row.get("Order Id", 0) or 0),
            order_status=str(row.get("Order Status", "")),
            shipping_mode=str(row.get("Shipping Mode", "")),
            days_shipping_real=int(row.get("Days for shipping (real)", 0) or 0),
            days_shipping_scheduled=int(row.get("Days for shipment (scheduled)", 0) or 0),
            delivery_status=str(row.get("Delivery Status", "")),
            late_delivery_risk=int(row.get("Late_delivery_risk", 0) or 0),
            market=str(row.get("Market", "")),
            order_region=str(row.get("Order Region", "")),
            order_country=str(row.get("Order Country", "")),
            category_name=str(row.get("Category Name", "")),
            department_name=str(row.get("Department Name", "")),
            customer_segment=str(row.get("Customer Segment", "")),
            customer_country=str(row.get("Customer Country", "")),
            product_name=str(row.get("Product Name", "")),
            product_price=float(row.get("Product Price", 0) or 0),
            sales=float(row.get("Sales", 0) or 0),
            order_profit_per_order=float(row.get("Order Profit Per Order", 0) or 0),
            benefit_per_order=float(row.get("Benefit per order", 0) or 0),
            order_item_quantity=int(row.get("Order Item Quantity", 0) or 0),
            order_date=str(row.get("order date (DateOrders)", "")),
            shipping_date=str(row.get("shipping date (DateOrders)", ""))
        )
        db.add(order)
        count += 1

        if count % 1000 == 0:
            db.commit()
            print(f"Inserted {count} records...")

    db.commit()
    db.close()
    print(f"Data loaded successfully - {count} records")

if __name__ == "__main__":
    load_csv_data("data/DataCoSupplyChainDataset.csv", limit=50000)