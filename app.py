import streamlit as st
from typing import Any, cast
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from lead_intake_agent import lead_agent

# 1. Page Configuration
st.set_page_config(
    page_title="AI Lead Intake & CRM Triage",
    page_icon="⚡",
    layout="wide"
)

# Helper function to prevent Streamlit from interpreting '$' as LaTeX math
def format_text(text: str) -> str:
    return str(text).replace("$", r"\$")

# 2. Sidebar: System Architecture & Health Indicators
with st.sidebar:
    st.title("⚡ System Architecture")
    st.markdown("Enterprise Lead Intake pipeline powered by **LangGraph** & **Groq**.")
    
    st.subheader("Connected Integrations")
    st.success("🟢 Google Sheets API (`AI_Lead_Intake_DB`)")
    st.success("🟢 ClickUp REST API (Task Automation)")
    st.info("🔵 Model: `openai/gpt-oss-120b`")
    
    st.divider()
    if st.button("Clear Chat Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_state = []
        st.rerun()

st.title("Enterprise AI Lead Qualification Portal")
st.caption("Conversational intake engine that qualifies client inquiries, updates database records, and provisions CRM tasks.")

# 3. State Management Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to our client onboarding portal. Could you share your name, company, and a brief overview of the project you'd like to build?"}
    ]

if "agent_state" not in st.session_state:
    st.session_state.agent_state = cast(
        list[HumanMessage | AIMessage | ToolMessage],
        [AIMessage(content="Hello! Welcome to our client onboarding portal. Could you share your name, company, and a brief overview of the project you'd like to build?")]
    )

# 4. Render Conversation History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(format_text(msg["content"]))

# 5. Handle User Input & LangGraph Execution
if user_input := st.chat_input("Tell us about your project requirements..."):
    # Display and record user prompt
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(format_text(user_input))
    
    # Append to graph state
    st.session_state.agent_state.append(HumanMessage(content=user_input))

    # Assistant response container
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        response_placeholder = st.empty()
        
        final_text = ""
        tool_status_text = []

        # Stream graph updates step-by-step
        with st.spinner("Processing request..."):
            events = lead_agent.stream(
                cast(Any, {"messages": st.session_state.agent_state}),
                stream_mode="values"
            )

            for event in events:
                messages = event.get("messages", [])
                if not messages:
                    continue
                
                latest_msg = messages[-1]

                # If the AI scheduled a tool execution
                if isinstance(latest_msg, AIMessage) and latest_msg.tool_calls:
                    for tc in latest_msg.tool_calls:
                        tool_status_text.append(f"🔧 Invoking `{tc['name']}` with arguments: `{tc['args']}`")
                    with status_placeholder.status("Executing External Workflows...", expanded=True) as status:
                        for log in tool_status_text:
                            st.write(log)
                        status.update(label="Workflows Executed Successfully!", state="complete")

                # If a Tool returned an execution output
                elif isinstance(latest_msg, ToolMessage):
                    tool_status_text.append(f"✅ Output: `{latest_msg.content}`")
                    with status_placeholder.status("Executing External Workflows...", expanded=False) as status:
                        for log in tool_status_text:
                            st.write(log)
                        status.update(label="Integrations Synchronized", state="complete")

                # Capture final conversational response
                elif isinstance(latest_msg, AIMessage) and latest_msg.content:
                    final_text = str(latest_msg.content)

            # Render final answer with LaTeX sanitization
            response_placeholder.markdown(format_text(final_text))
            
            # Persist response to history
            st.session_state.messages.append({"role": "assistant", "content": final_text})
            st.session_state.agent_state.append(AIMessage(content=final_text))