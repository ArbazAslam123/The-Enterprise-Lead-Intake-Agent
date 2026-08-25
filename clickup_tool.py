import os
import requests
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()

def get_clickup_credentials():
    api_key = (
        st.secrets.get("CLICKUP_API_KEY") 
        if hasattr(st, "secrets") and "CLICKUP_API_KEY" in st.secrets 
        else os.environ.get("CLICKUP_API_KEY")
    )
    list_id = (
        st.secrets.get("CLICKUP_LIST_ID") 
        if hasattr(st, "secrets") and "CLICKUP_LIST_ID" in st.secrets 
        else os.environ.get("CLICKUP_LIST_ID")
    )
    return api_key, list_id

class ClickUpTaskSchema(BaseModel):
    client_name: str = Field(description="Full name of the client or lead")
    company: str = Field(description="Company or business name, or 'Individual'")
    budget: str = Field(description="Estimated budget, e.g., 'USD 10,000'")
    project_summary: str = Field(description="Summary of project requirements")
    urgency_level: str = Field(default="normal", description="Priority level: urgent, high, normal, or low")

@tool("create_clickup_task", args_schema=ClickUpTaskSchema)
def create_clickup_task(
    client_name: str,
    company: str,
    budget: str,
    project_summary: str,
    urgency_level: str = "normal",
    **kwargs
) -> str:
    """Create a new sales follow-up task in ClickUp for an incoming qualified lead."""
    api_key, list_id = get_clickup_credentials()
    
    if not api_key or not list_id:
        return "ClickUp credentials missing from environment or Streamlit secrets."

    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    headers = {
        "Authorization": str(api_key).strip(),
        "Content-Type": "application/json"
    }

    priority_map = {"urgent": 1, "high": 2, "normal": 3, "low": 4}
    priority_val = priority_map.get(urgency_level.lower(), 3)

    task_description = (
        f"### New Inbound Lead Details\n\n"
        f"- **Client Name:** {client_name}\n"
        f"- **Company:** {company}\n"
        f"- **Budget:** {budget}\n\n"
        f"**Project Summary:**\n{project_summary}\n\n"
        f"---\n*Created automatically via AI Lead Intake Agent.*"
    )

    payload = {
        "name": f"Lead: {client_name} ({company}) - {budget}",
        "description": task_description,
        "priority": priority_val,
        "tags": ["lead-intake", "ai-routed"],
        "status": "to do"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            data = response.json()
            return f"ClickUp task created successfully. URL: {data.get('url', '')}"
        return f"ClickUp API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Failed to connect to ClickUp API. Error: {str(e)}"