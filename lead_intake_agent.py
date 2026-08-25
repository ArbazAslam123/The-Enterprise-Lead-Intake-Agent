import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

# Import out custom verified tools
from google_sheets_tool import log_lead_to_sheets
from clickup_tool import create_clickup_task

load_dotenv()

# State Definition
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# model setup and tool binding
api_key = os.getenv("GROQ_API_KEY")
llm= ChatGroq(
    api_key=SecretStr(api_key) if api_key is not None else None, 
    model="openai/gpt-oss-120b",
    temperature=0.1
)

tools= [log_lead_to_sheets, create_clickup_task]
llm_with_tools= llm.bind_tools(tools)

# System Prompt Instruction
SYSTEM_PROMPT="""YOu are a Enterprise Lead Intake Specialist for an AI & Data Engineering Agency.
Your objective is to collect 4 specific data points from incoming prospects:
1. Full Name
2. Company Name (or 'Individual' if none)
3. Project Scope / Summary
4. Estimated Budget

Rules:
- Never wrap dollar values in raw quotes that trigger math formatting (e.g., do NOT write "$10k-20k$" or "$5,000$").
- Always format currency as either 'USD 10,000' or '\$10,000 - \$20,000' using plain text.
- If any required information is missing, have a natural conversation and ask for the missing details.
- Once you have All 4 details, immediately invoke BOTH 'log_lead_to_sheets' AND 'create_clickup_task'.
- After tools execute, confirm the registration clearly and professionally to the user.
"""

# Assistant Node definition
def assistant_node(state: AgentState):
    messages = state["messages"]

    # Inject system instructions at index 0 if not already present
    if not any(hasattr(m, "content") and "Enterprise Lead Intake" in str(m.content) for m in messages):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Workflow Graph Assembly
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
        {"messages": [("user", test_query)]},
        stream_mode="values"
    )
    
    for event in events:
        last_msg = event["messages"][-1]
        last_msg.pretty_print()