import os
from datetime import datetime
import gspread
import streamlit as st
from pydantic import BaseModel, Field
from google.oauth2.service_account import Credentials
from langchain_core.tools import tool

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_FILE = "google_credentials.json"
SPREADSHEET_NAME = "AI_Lead_Intake_DB"

def get_sheets_client():
    if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        return gspread.authorize(creds)
        
    raise FileNotFoundError("Google Cloud credentials not found in st.secrets or local JSON.")

class SheetLeadSchema(BaseModel):
    client_name: str = Field(description="Full name of the client or lead")
    company: str = Field(description="Company or business name, or 'Individual'")
    budget: str = Field(description="Estimated budget, e.g., 'USD 10,000'")
    project_summary: str = Field(description="Summary of project requirements")

@tool("log_lead_to_sheets", args_schema=SheetLeadSchema)
def log_lead_to_sheets(client_name: str, company: str, budget: str, project_summary: str, **kwargs) -> str:
    """Log a qualified prospective lead into the Google Sheet database."""
    try:
        client = get_sheets_client()
        sheet = client.open(SPREADSHEET_NAME).sheet1
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "New Lead"
        
        row_data = [timestamp, client_name, company, budget, project_summary, status]
        sheet.append_row(row_data)
        
        return f"Successfully logged lead '{client_name}' from '{company}' to Google Sheets."
    except Exception as e:
        return f"Failed to log lead to Google Sheets. Error: {str(e)}"