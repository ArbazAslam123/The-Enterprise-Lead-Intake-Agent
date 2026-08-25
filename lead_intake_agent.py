import os
from typing import TypedDict, Annotated
import streamlit as st
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from google_sheets_tool import get_sheets_client
from clickup_tool import create_clickup_task

load_dotenv()

# Retrieve API key securely
groq_api_key = (
    st.secrets.get("GROQ_API_KEY") 
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets 
    else os.environ.get("GROQ_API_KEY")
)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Initialize model
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=SecretStr(groq_api_key) if isinstance(groq_api_key, str) else None,
    temperature=0.1
)

tools = [get_sheets_client, create_clickup_task]
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are an Enterprise Lead Intake Specialist for an AI & Data Engineering Agency.
Your objective is to collect 4 specific data points from incoming prospects:
1. Full Name
2. Company Name (or 'Individual' if none)
3. Project Scope / Summary
4. Estimated Budget

Formatting Rules:
- Never wrap dollar values in raw quotes that trigger math formatting (e.g., do NOT write "$10k-20k$" or "$5,000$").
- Always format currency as either 'USD 10,000' or '\$10,000 - \$20,000' using plain text.
- If any required information is missing, converse naturally to request the remaining details.
- Once you have ALL 4 details, invoke BOTH `log_lead_to_sheets` AND `create_clickup_task`.
- After tools execute, confirm the registration clearly and professionally to the user.
"""

def assistant_node(state: AgentState):
    raw_messages = list(state["messages"])
    
    # Ensure system message is properly prepended as a LangChain BaseMessage
    if not raw_messages or not isinstance(raw_messages[0], SystemMessage):
        formatted_messages = [SystemMessage(content=SYSTEM_PROMPT)] + raw_messages
    else:
        formatted_messages = raw_messages
        
    response = llm_with_tools.invoke(formatted_messages)
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("assistant", assistant_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "assistant")
workflow.add_conditional_edges("assistant", tools_condition)
workflow.add_edge("tools", "assistant")

lead_agent = workflow.compile()
# Local Terminal Execution
if __name__ == "__main__":
    print("--- Running Lead Intake Agent Test ---\n")
    
    test_query = (
        "Hi! My name is Sophia Reed from Nexus Logistics. "
        "We need an automated warehouse dispatch pipeline using BigQuery and n8n. "
        "Our allocated budget is $20,000, and we want to start next month."
    )
    
    print(f"👤 User: {test_query}\n")
    
    events = lead_agent.stream(
        {"messages": [HumanMessage(content=test_query)]},
        stream_mode="values"
    )
    
    for event in events:
        last_msg = event["messages"][-1]
        last_msg.pretty_print()