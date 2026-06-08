from dotenv import load_dotenv
load_dotenv(override=True)

import sys
import os
import json
import httpx
from datetime import datetime
from typing import TypedDict, Annotated

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrockConverse
from app.database.connection import SessionLocal
from app.database.models import RiskReport

API_BASE = "http://localhost:8000"

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    risk_data: dict
    delayed_orders: list
    disruptions: list
    summary: dict
    report: str
    alerts_sent: bool

token = os.getenv('AWS_BEARER_TOKEN_BEDROCK', '')
os.environ['AWS_BEARER_TOKEN_BEDROCK'] = token
print(f"Bedrock token loaded: {token[:20]}...{token[-6:] if len(token) > 26 else '(too short)'}")

llm = ChatBedrockConverse(
    model="amazon.nova-micro-v1:0",
    region_name="us-east-1",
)

# Node 1 — Fetch risk data
def fetch_risk_data(state: AgentState) -> AgentState:
    print("Fetching supplier risk data...")

    with httpx.Client() as client:
        risk_data = client.get(f"{API_BASE}/suppliers/risk").json()
        delayed_orders = client.get(f"{API_BASE}/orders/delayed").json()
        disruptions = client.get(f"{API_BASE}/orders/disruptions").json()
        summary = client.get(f"{API_BASE}/suppliers/summary").json()

    print(f"Fetched {len(risk_data)} risky suppliers")
    print(f"Fetched {len(delayed_orders)} delayed orders")

    return {
        **state,
        "risk_data": risk_data,
        "delayed_orders": delayed_orders,
        "disruptions": disruptions,
        "summary": summary,
    }

# Node 2 — Analyze risk
def analyze_risk(state: AgentState) -> AgentState:
    print("Analyzing risk patterns...")
    
    risk_data = state["risk_data"]
    delayed_orders = state["delayed_orders"]
    disruptions = state["disruptions"]
    summary = state["summary"]
    
    analysis_prompt = f"""
You are a supply chain risk analyst. Analyze this data and identify:
1. Highest risk product categories and markets
2. Delivery performance patterns
3. Late delivery risk concentrations
4. Profit impact of delays
5. Immediate actions needed

HIGH RISK CATEGORIES BY MARKET:
{json.dumps(risk_data[:5], indent=2)}

DELAYED ORDERS (top 5):
{json.dumps(delayed_orders[:5], indent=2)}

DISRUPTION PATTERNS:
{json.dumps(disruptions[:5], indent=2)}

OVERALL SUMMARY:
{json.dumps(summary, indent=2)}

Focus on:
- Which markets have highest late delivery risk
- Which categories are most affected
- Financial impact (profit per order)
- Recommended actions for procurement team
"""
    
    response = llm.invoke([
        SystemMessage(content="You are an expert supply chain risk analyst."),
        HumanMessage(content=analysis_prompt)
    ])
    
    return {
        **state,
        "messages": [response],
        "report": response.content
    }
def generate_report(state: AgentState) -> AgentState:
    print("Generating final report...")

    report_prompt = f"""
    Based on this analysis:
    {state["report"]}

    Generate a professional Supply Chain Risk Intelligence Report with:

    # Supply Chain Risk Intelligence Report
    ## Executive Summary
    ## Critical Alerts
    ## Top Risky Suppliers
    ## Disruption Analysis
    ## Recommended Actions
    ## Conclusion

    Be specific with supplier IDs, numbers, and actionable recommendations.
    """

    response = llm.invoke([
        SystemMessage(content="You are a supply chain risk reporting expert."),
        HumanMessage(content=report_prompt)
    ])

    return {
        **state,
        "report": response.content,
        "alerts_sent": False,
    }

# Node 4 — Save report, send email, upload to Drive
def save_report(state: AgentState) -> AgentState:
    print("Saving report to database...")

    db = SessionLocal()
    report_record = RiskReport(
        title="Daily Supply Chain Risk Report",
        content=state["report"],
        suppliers_analyzed=len(state["risk_data"]),
        critical_alerts=len([
            o for o in state["delayed_orders"]
            if o.get("delay_days", 0) > 3
        ]),
    )
    db.add(report_record)
    db.commit()
    print("Report saved to database ✅")

    # Save to markdown file
    os.makedirs("reports", exist_ok=True)
    filename = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = f"reports/{filename}"
    with open(filepath, "w") as f:
        f.write(state["report"])
    print(f"Report saved to {filepath} ✅")

    # Generate short email summary via LLM
    print("Generating email summary...")
    summary_response = llm.invoke([
        SystemMessage(content="You are a supply chain analyst."),
        HumanMessage(content=f"""
        Based on this full report write a SHORT email summary (max 150 words) with:
        - 3 most critical alerts
        - Top 2 risky suppliers
        - 2 immediate actions needed

        Be concise and direct. No markdown formatting.

        Report:
        {state["report"]}
        """)
    ])
    email_summary = summary_response.content
    print("Email summary generated ✅")

    from app.agent.gmail_integration import send_email, save_to_drive

    print("Sending email alert...")
    send_email(
        "maazulhasan@usf.edu",
        f"Daily Supply Chain Risk Report — {datetime.now().strftime('%B %d, %Y')}",
        email_summary,
        attachment_path=filepath,
    )
    report_record.sent_via_email = True
    print("Email sent ✅")

    print("Uploading report to Google Drive...")
    save_to_drive(filename, state["report"])
    report_record.stored_in_drive = True
    print("Saved to Google Drive ✅")

    db.commit()
    db.close()

    return {**state, "alerts_sent": True}


def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("fetch_data", fetch_risk_data)
    graph.add_node("analyze", analyze_risk)
    graph.add_node("generate_report", generate_report)
    graph.add_node("save_report", save_report)

    graph.add_edge(START, "fetch_data")
    graph.add_edge("fetch_data", "analyze")
    graph.add_edge("analyze", "generate_report")
    graph.add_edge("generate_report", "save_report")
    graph.add_edge("save_report", END)

    return graph.compile()


if __name__ == "__main__":
    agent = build_agent()

    initial_state = {
        "messages": [],
        "risk_data": {},
        "delayed_orders": [],
        "disruptions": [],
        "summary": {},
        "report": "",
        "alerts_sent": False,
    }

    result = agent.invoke(initial_state)
    print("\n" + "=" * 60)
    print(result["report"])
    print("=" * 60)
