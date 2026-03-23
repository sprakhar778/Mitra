import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.graph.graph import create_workflow_graph
from src.graph.state import AgentState

import streamlit as st

from src.modules.image.text_to_image import get_text_to_image_module
from src.modules.image.image_to_text import get_image_to_text_module
from src.modules.speech.speech_to_text import get_speech_to_text_module
from src.modules.speech.text_to_speech import get_text_to_speech_module


import asyncio


#make an app to test the graph


import streamlit as st
from langchain_core.messages import HumanMessage
from src.graph.graph import create_workflow_graph
from src.graph.state import AgentState

# Cache compiled graph
@st.cache_resource
def get_graph():
    return create_workflow_graph().compile()

graph = get_graph()

st.set_page_config(page_title="AI Companion Graph Tester", layout="wide")

st.title("🤖 AI Companion Graph Tester")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""

# Sidebar for inputs
st.sidebar.header("Inputs")

uploaded_image = st.sidebar.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
uploaded_audio = st.sidebar.file_uploader("Upload Audio", type=["wav", "mp3"])

user_input = st.text_input("Enter your message")

# Display chat history
st.subheader("Conversation")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# Process input
if st.button("Send") and (user_input or uploaded_image or uploaded_audio):

    # Prepare state
    state = AgentState(
        messages=[HumanMessage(content=user_input if user_input else "")],
        summary=st.session_state.summary,
        workflow="conversation",
        audio_buffer=uploaded_audio.read() if uploaded_audio else b"",
        image_path="temp_image.jpg" if uploaded_image else "",
        memory_context=""
    )

    if uploaded_image:
        image_bytes = uploaded_image.read()
        with open("temp_image.jpg", "wb") as f:
            f.write(image_bytes)

    # Async runner
    def run_async(coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    # Run graph
    result = run_async(graph.ainvoke(state))
        # Extract response
    response = result["messages"][-1].content

    # Update session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.summary = result.get("summary", "")

    # Refresh UI
    st.rerun()

# Display summary
if st.session_state.summary:
    st.sidebar.subheader("Conversation Summary")
    st.sidebar.write(st.session_state.summary)

# streamlit run src/interface/app.py