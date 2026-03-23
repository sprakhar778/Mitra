import sys
import os
import asyncio
import streamlit as st
from langchain_core.messages import HumanMessage

# Fix import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Graph imports
from src.graph.graph import create_workflow_graph
from src.graph.state import AgentState

# Modules
from src.modules.image.image_to_text import get_image_to_text_module
from src.modules.speech.speech_to_text import get_speech_to_text_module


# -------------------- GRAPH SETUP --------------------

@st.cache_resource
def get_graph():
    return create_workflow_graph().compile()

graph = get_graph()


# -------------------- ASYNC RUNNER --------------------

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


# -------------------- UI SETUP --------------------

st.set_page_config(page_title="AI Companion Graph Tester", layout="wide")

st.title("🤖 AI Companion Graph Tester")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""


# -------------------- SIDEBAR --------------------

st.sidebar.header("Inputs")

uploaded_image = st.sidebar.file_uploader(
    "Upload Image", type=["png", "jpg", "jpeg"]
)

uploaded_audio = st.sidebar.file_uploader(
    "Upload Audio", type=["wav", "mp3"]
)


# -------------------- INPUT --------------------

user_input = st.text_input("Enter your message")


# -------------------- CHAT DISPLAY --------------------

st.subheader("Conversation")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -------------------- MAIN LOGIC --------------------

if st.button("Send") and (user_input or uploaded_image or uploaded_audio):

    image_text = ""
    audio_text = ""

    # 🔄 Process Image
    if uploaded_image:
        with st.spinner("🖼️ Processing image..."):
            image_module = get_image_to_text_module()
            image_text = run_async(
                image_module.analyze_image(uploaded_image.read())
            )

    # 🔄 Process Audio
    if uploaded_audio:
        with st.spinner("🎤 Transcribing audio..."):
            speech_module = get_speech_to_text_module()
            audio_text = run_async(
                speech_module.transcribe(uploaded_audio.read())
            )

    # 🔗 Combine all inputs safely
    combined_input = " ".join(
        filter(None, [user_input, image_text, audio_text])
    )

    # 🧠 Prepare state
    state = AgentState(
        messages=[HumanMessage(content=combined_input)],
        summary=st.session_state.summary,
        workflow="conversation",
        audio_buffer="",
        image_path="",
        memory_context=""
    )

    # 🤖 Run Graph
    with st.spinner("🤖 Thinking..."):
        result = run_async(graph.ainvoke(state))

    response = result["messages"][-1].content

    # 💬 Update chat
    st.session_state.messages.append({
        "role": "user",
        "content": combined_input
    })

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # 🧾 Update summary
    st.session_state.summary = result.get("summary", "")

    st.rerun()


# -------------------- SUMMARY --------------------

if st.session_state.summary:
    st.sidebar.subheader("Conversation Summary")
    st.sidebar.write(st.session_state.summary)


# Run command:
# streamlit run src/interface/app.py