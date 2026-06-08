# Project Context — Supply Chain Risk Intelligence Platform

## What This Project Is
An autonomous AI agent that monitors supply chain data, detects risks, generates professional intelligence reports, and delivers them via email and Google Drive — automatically.

## Project Location
C:\Users\owner\Desktop\supply_chain_agent

## Tech Stack
- Python 3.12 + uv package manager
- FastAPI + Uvicorn (REST API)
- PostgreSQL 15 (Docker container)
- SQLAlchemy (ORM)
- LangGraph (agent framework)
- AWS Bedrock — Amazon Nova Micro (LLM)
- Gmail API + Google Drive API (OAuth2)
- Docker + Docker Compose
- Deployed on AWS EC2 (IP: 54.91.221.67)

## Project Structure
```
supply_chain_agent/
├── app/
│   ├── api/
│   │   ├── main.py          # FastAPI app
│   │   └── routes.py        # 5 endpoints
│   ├── agent/
│   │   ├── agent.py         # LangGraph 4-node agent
│   │   └── gmail_integration.py  # Gmail + Drive
│   └── database/
│       ├── models.py        # Order + RiskReport tables
│       ├── connection.py    # SQLAlchemy connection
│       └── load_data.py     # CSV loader
├── data/
│   ├── DataCoSupplyChainDataset.csv  # 180,519 rows, 53 cols
│   ├── DescriptionDataCoSupplyChain.csv  # column descriptions
│   └── tokenized_access_logs.csv  # not used
├── reports/                 # generated .md reports
├── docker-compose.yml
├── Dockerfile
└── .env                     # never commit this
```

## Database Schema

### orders table (loaded from DataCo Kaggle dataset)
- id, order_id, order_status, shipping_mode
- days_shipping_real, days_shipping_scheduled
- delivery_status, late_delivery_risk
- market, order_region, order_country
- category_name, department_name
- customer_segment, customer_country
- product_name, product_price, sales
- order_profit_per_order, benefit_per_order
- order_item_quantity, order_date, shipping_date

### risk_reports table
- id, title, content
- suppliers_analyzed, critical_alerts
- generated_at, sent_via_email, stored_in_drive

## FastAPI Endpoints (running at port 8000)
- GET /                    → health check
- GET /suppliers/risk      → top 10 by avg risk, grouped by category
- GET /orders/delayed      → delay_days > 5
- GET /orders/disruptions  → grouped by type and severity
- GET /suppliers/summary   → total orders, avg delay, high risk count, total value

## LangGraph Agent — 4 Nodes
1. fetch_risk_data  → calls all 4 FastAPI endpoints via httpx
2. analyze_risk     → sends data to LLM, returns risk analysis
3. generate_report  → LLM formats professional markdown report
4. save_report      → saves to DB, saves .md file, generates email
                      summary via LLM, sends email with attachment,
                      saves to Google Drive

## LLM Configuration
- Model: AWS Bedrock Amazon Nova Micro (amazon.nova-micro-v1:0)
- Auth: AWS_BEARER_TOKEN_BEDROCK env var
- os.environ['AWS_BEARER_TOKEN_BEDROCK'] set before boto3 client
- Uses ChatBedrockConverse from langchain_aws

## Gmail Integration
- OAuth2 with token.json (expires — delete and rerun gmail_integration.py)
- Sends HTML email with full summary + .md attachment
- LLM generates 150-word email summary
- token.json and credentials.json are gitignored

## Google Drive Integration
- Files appear in Drive root
- Uploads as text/plain with timestamp filename

## Docker Compose
- supply_chain_postgres container (postgres:15)
- supply_chain_api container
- Containers use service name "postgres" not "localhost" internally
- Scripts run directly use "localhost"

## AWS EC2
- Instance: t3.micro, Amazon Linux 2023
- Public IP: 54.91.221.67
- Port 8000 open in security group
- Key pair: supply-chain-key.pem (in Downloads)
- docker-compose up --build -d running

## GitHub
https://github.com/maaz-masood/supply-chain-risk-agent

## .env Structure (never commit)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/supply_chain
OPENROUTER_API_KEY=...
AWS_BEARER_TOKEN_BEDROCK=bedrock-api-key-...
AWS_DEFAULT_REGION=us-east-1
```

## How To Run Locally
```bash
# Terminal 1 - Start PostgreSQL
docker start supply_chain_postgres

# Terminal 2 - Start FastAPI
uv run uvicorn app.api.main:app --reload

# Terminal 3 - Run agent
uv run app/agent/agent.py
```

## How To Run With Docker Compose
```bash
docker-compose up --build -d
uv run app/database/load_data.py
uv run app/agent/agent.py
```

## Common Issues & Fixes
- Connection closed MCP error → never run server.py directly
- Max turns exceeded → set max_turns=30
- Gmail token expired → Remove-Item token.json → rerun gmail_integration.py
- postgres vs localhost → use "postgres" inside Docker, "localhost" outside
- .env not loading → use Set-Content to write from PowerShell

## Current Status
- 50,000 rows loading from DataCo dataset (in progress)
- AWS Bedrock Nova Micro integrated as LLM
- Full pipeline working locally and on AWS EC2
- Gmail alerts working with .md attachment
- Google Drive saving working

## Remaining Tasks
- Finish loading DataCo dataset
- Update routes.py for new schema columns
- Update agent prompts for new data structure
- Push final code to GitHub
- Write LinkedIn post
- Record demo video
