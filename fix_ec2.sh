#!/bin/bash
set -e

export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/supply_chain

# Adjust this to your project path on EC2
PROJECT_DIR="/home/ec2-user/supply_chain_agent"
cd "$PROJECT_DIR"

echo "=============================="
echo " Step 1: Recreate orders table"
echo "=============================="
uv run python -c "
from app.database.connection import engine
from app.database.models import Base, Order
Order.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(engine)
print('orders table recreated')
"

echo ""
echo "=============================="
echo " Step 2: Load DataCo CSV"
echo "=============================="
uv run app/database/load_data.py

echo ""
echo "=============================="
echo " Step 3: Verify record count"
echo "=============================="
uv run python -c "
from app.database.connection import SessionLocal
from app.database.models import Order
db = SessionLocal()
count = db.query(Order).count()
print(f'Records in orders table: {count}')
db.close()
"

echo ""
echo "Done."
