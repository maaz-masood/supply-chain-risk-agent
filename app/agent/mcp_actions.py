from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.mcp import MCPServerSse

# Gmail MCP server
gmail_server = MCPServerSse(
    params={
        "url": "https://gmailmcp.googleapis.com/mcp/v1",
    }
)

# Google Drive MCP server  
drive_server = MCPServerSse(
    params={
        "url": "https://drivemcp.googleapis.com/mcp/v1",
    }
)

async def send_email_alert(report_content: str, recipient_email: str):
    """Send risk report via Gmail MCP"""
    
    async with gmail_server as gmail:
        agent = Agent(
            name="Email Agent",
            model=OpenAIChatCompletionsModel(
                model="openrouter/auto",
                openai_client=AsyncOpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1"
                )
            ),
            instructions="""You are an email assistant.
            Send the supply chain risk report via email.
            Format it professionally.""",
            mcp_servers=[gmail]
        )
        
        result = await Runner.run(
            agent,
            f"""Send an email to {recipient_email} with:
            Subject: Daily Supply Chain Risk Intelligence Report
            Body: {report_content[:2000]}
            
            Send it now.""",
            max_turns=10
        )
        
        return result.final_output

async def save_to_drive(report_content: str, filename: str):
    """Save risk report to Google Drive MCP"""
    
    async with drive_server as drive:
        agent = Agent(
            name="Drive Agent",
            model=OpenAIChatCompletionsModel(
                model="openrouter/auto",
                openai_client=AsyncOpenAI(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1"
                )
            ),
            instructions="""You are a Google Drive assistant.
            Save documents to Google Drive.""",
            mcp_servers=[drive]
        )
        
        result = await Runner.run(
            agent,
            f"""Create a new Google Doc called '{filename}'
            with this content:
            {report_content[:3000]}
            
            Save it to Google Drive now.""",
            max_turns=10
        )
        
        return result.final_output

if __name__ == "__main__":
    # Test email
    test_report = "Test Supply Chain Risk Report - Critical alerts detected"
    asyncio.run(send_email_alert(
        test_report, 
        "maazulhasan@usf.edu"
    ))