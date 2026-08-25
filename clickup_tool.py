import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

# Ensure environment variables are loaded
load_dotenv()

CLICKUP_API_KEY = os.environ.get("CLICKUP_API_KEY")
CLICKUP_LIST_ID = os.environ.get("CLICKUP_LIST_ID")

@tool
def create_clickup_task(
    client_name: str,
    company: str,
    budget: str,
    project_summary: str,
    urgency_level: str = "normal"
) -> str:
    """
    Create a new sales follow-up task in ClickUp for an incoming qualified lead.

    Args:
        client_name: Full name of the lead.
        company: Business or organization name.
        budget: Estimated client budget (e.g., '$10,000').
        project_summary: Concise description of requirements and scope.
        urgency_level: Priority level - 'urgent', 'high', 'normal', or 'low'.
    """
    if not CLICKUP_API_KEY or not CLICKUP_LIST_ID:
        return f"Configuration Error: Missing CLICKUP_API_KEY ({bool(CLICKUP_API_KEY)}) or CLICKUP_LIST_ID ({bool(CLICKUP_LIST_ID)}) in .env"

    url = f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"

    headers = {
        "Authorization": CLICKUP_API_KEY.strip(),
        "Content-Type": "application/json"
    }

    priority_map = {
        "urgent": 1,
        "high": 2,
        "normal": 3,
        "low": 4
    }
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
            task_url = data.get("url", "")
            return f"Success: ClickUp task created. URL: {task_url}"
        else:
            return f"ClickUp API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Network/Connection Error: {str(e)}"


# --- DIRECT EXECUTION TEST BLOCK ---
if __name__ == "__main__":
    
    test_payload = {
        "client_name": "Babar Azam",
        "company": "PCB",
        "budget": "$67,000",
        "project_summary": "End-to-end multi-agent orchestration for supply chain telemetry.",
        "urgency_level": "high"
    }
    
    result = create_clickup_task.invoke(test_payload)
    print("\n--- Output ---")
    print(result)