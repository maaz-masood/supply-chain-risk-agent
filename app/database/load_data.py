import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.connection import SessionLocal, create_tables
from app.database.models import Order

def load_csv_data(filepath: str):
    create_tables()
    db = SessionLocal()
    
    df = pd.read_csv(filepath)
    print(f"Loading {len(df)} records...")
    
    for _, row in df.iterrows():
        # Check if order already exists
        existing = db.query(Order).filter(
            Order.order_id == str(row["Order_ID"])
        ).first()
        
        if not existing:
            order = Order(
                order_id=str(row["Order_ID"]),
                buyer_id=str(row["Buyer_ID"]),
                supplier_id=str(row["Supplier_ID"]),
                product_category=str(row["Product_Category"]),
                quantity_ordered=int(row["Quantity_Ordered"]),
                order_date=pd.to_datetime(row["Order_Date"]).date(),
                dispatch_date=pd.to_datetime(row["Dispatch_Date"]).date(),
                delivery_date=pd.to_datetime(row["Delivery_Date"]).date(),
                shipping_mode=str(row["Shipping_Mode"]),
                order_value_usd=float(row["Order_Value_USD"]),
                delay_days=int(row["Delay_Days"]),
                disruption_type=str(row["Disruption_Type"]),
                disruption_severity=str(row["Disruption_Severity"]),
                historical_disruption_count=int(row["Historical_Disruption_Count"]),
                supplier_reliability_score=float(row["Supplier_Reliability_Score"]),
                supply_risk=float(row["Supply_Risk_Flag"])
            )       
            db.add(order)
    
    db.commit()
    db.close()
    print("Data loaded successfully ✅")

if __name__ == "__main__":
    load_csv_data("data/supply_chain_data.csv")