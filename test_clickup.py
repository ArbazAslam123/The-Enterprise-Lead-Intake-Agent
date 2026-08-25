from clickup_tool import create_clickup_task

print("Testing direct ClickUp task creation...")

result = create_clickup_task.invoke({
    "client_name": "Marcus Vance",
    "company": "Vance Dynamics",
    "budget": "$25,000",
    "project_summary": "End-to-end multi-agent orchestration for supply chain telemetry.",
    "urgency_level": "high"
})

print(result)