from google_sheets_tool import log_lead_to_sheets

print("Testing direct Google Sheets insertion...")

# Invoke the tool directly using .invoke()
result = log_lead_to_sheets.invoke({
    "name": "Sarah Connor",
    "company": "Cyberdyne Systems",
    "budget": "$15,000",
    "project_request": "Automated workflow pipeline for server monitoring."
})

print(result)