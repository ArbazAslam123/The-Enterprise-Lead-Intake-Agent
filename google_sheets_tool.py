import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from langchain_core.tools import tool

# Define the scopes required to read/write to Google Sheets and Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_FILE = "google_credentials.json"
SPREADSHEET_NAME = "AI_Lead_Intake_DB"

def get_sheets_client():
    """Authenticates with Google Cloud using the Service Account JSON."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Missing {CREDENTIALS_FILE} in root directory.")
    
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

@tool
def log_lead_to_sheets(name: str, company: str, budget: str, project_request: str) -> str:
    """
    Log a qualified lead into the Google Sheet database.
    
    Args:
        name: Full name of the client/lead.
        company: Company or business name (use 'N/A' if individual).
        budget: Estimated budget (e.g., '$5,000' or '$10k-$20k').
        project_request: A concise summary of what the client wants to build.
    """
    try:
        client = get_sheets_client()
        sheet = client.open(SPREADSHEET_NAME).sheet1
        
        # Format the row data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "New Lead"
        
        row_data = [timestamp, name, company, budget, project_request, status]
        
        # Append the row to the next available line in the sheet
        sheet.append_row(row_data)
        
        return f"Successfully logged lead '{name}' from '{company}' to Google Sheets."
    except Exception as e:
        return f"Failed to log lead to Google Sheets. Error: {str(e)}"