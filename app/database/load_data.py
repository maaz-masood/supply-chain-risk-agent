import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.connection import SessionLocal, create_tables
from app.database.models import Order

def _disruption_severity(delay: int) -> str:
    if delay >= 10:
        return "high"
    elif delay >= 5:
        return "medium"
    return "low"

def load_csv_data(filepath: str, limit: int = 50000):
    create_tables()
    db = SessionLocal()
    count = 0

    df = pd.read_csv(filepath, encoding='latin-1', nrows=limit)
    print(f"Loading {len(df)} records...")

    for _, row in df.iterrows():
        real = int(row.get("Days for shipping (real)", 0) or 0)
        scheduled = int(row.get("Days for shipment (scheduled)", 0) or 0)
        delay = max(0, real - scheduled)
        late_risk = int(row.get("Late_delivery_risk", 0) or 0)

        order = Order(
            order_id=int(row.get("Order Id", 0) or 0),
            supplier_id=int(row.get("Department Id", 0) or 0),
            product_category=str(row.get("Category Name", "")),
            supplier_reliability_score=round(1.0 - late_risk, 2),
            supply_risk=float(late_risk),
            delay_days=delay,
            disruption_type=str(row.get("Delivery Status", "")),
            disruption_severity=_disruption_severity(delay),
            order_value_usd=float(row.get("Sales", 0.0) or 0.0),
        )
        db.add(order)
        count += 1
        if count % 1000 == 0:
            db.commit()
            print(f"Inserted {count} records...")

    db.commit()
    db.close()
    print("Data loaded successfully ✅")

if __name__ == "__main__":
    load_csv_data("data/DataCoSupplyChainDataset.csv", limit=50000)
