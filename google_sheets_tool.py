import os
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from langchain_core.tools import tool

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_FILE = "google_credentials.json"
SPREADSHEET_NAME = "AI_Lead_Intake_DB"

def get_sheets_client():
    """Authenticates via Streamlit Secrets (Cloud) or JSON file (Local)."""
    # 1. Check if running on Streamlit Cloud with configured secrets
    if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    
    # 2. Fallback to local JSON file for local execution
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        return gspread.authorize(creds)
        
    raise FileNotFoundError("Google Cloud credentials not found in st.secrets or local JSON.")