   # Mitra: Your AI Companion

   Mitra is an advanced, multi-modal AI Companion application built with Streamlit and LangGraph. It simulates a Turing Test-like environment where users interact with "Mitra", a persona-driven AI acting as a Machine Learning Engineer. The application features advanced workflow routing, voice and image processing, and persistent long-term memory.


## 🎬 Demo

[![Watch Demo](https://img.youtube.com/vi/zkn-iF-Yv_A/maxresdefault.jpg)](https://youtu.be/JfIYeL-DdNQ?si=IgYYYLBc-45puYt6)


   ## Features

   - **Multi-Modal Interaction**: Chat via text, upload images (processed by an image-to-text module), or upload audio files (transcribed using Deepgram).
   - **Persistent Memory**: Automatically extracts, stores, and injects user facts into the conversation context using Qdrant vector database.
   - **Workflow State Management**: Powered by LangGraph for robust, scalable state management, including memory extraction, conditional routing, and conversation summarization.
   - **Persona Roleplay**: Engages users naturally as Mitra, maintaining character consistency throughout interactions without revealing her AI nature.
   - **Dynamic Summarization**: Automatically summarizes conversations to maintain context without bursting token limits.

   ## Project Architecture

   Mitra uses a node-based architecture orchestrated by LangGraph (`src/graph`):
   - `memory_extraction_node`: Identifies and records important facts about the user.
   - `router_node`: Decides the appropriate sub-workflow based on user input (text, image, audio).
   - `memory_injection_node`: Retrieves user facts to provide personalized responses.
   - `conversation_node`, `image_node`, `audio_node`: Specialized nodes for handling different modalities.
   - `summarize_conversation_node`: Compresses chat history as the conversation grows.

   ## 🌐 Interfaces

   Mitra supports two interaction interfaces:

   1. 💬 Chainlit (Local UI)
   Interactive chat interface
   Supports text, image, and audio uploads
   Ideal for development and testing
   2. 📱 WhatsApp Integration
   Chat with Mitra directly via WhatsApp
   Built using WhatsApp API
   Uses ngrok to expose local server
   Supports:
   Message streaming
   Media handling (audio/images)
   Real-time responses
   ## Prerequisites

   - Python >= 3.12
   - API keys for LLM providers (OpenAI, Groq, Google GenAI, etc.)
   - Deepgram API key (for audio transcription)
   - Setup a `.env` file containing the necessary environment variables (refer to `.env.example`).

   ## Installation

   1. Clone the repository and navigate to the project root:
      ```bash
      cd mitra
      ```

   2. (Optional but recommended) Create and activate a virtual environment:
      ```bash
      python -m venv .venv
      source .venv/bin/activate  # On Windows: .venv\Scripts\activate
      ```

   3. Install dependencies:
      You can use `uv` or `pip` to install the requirements from `pyproject.toml`:
      ```bash
      pip install -e .
      ```

   ## Usage

   Start the Chainlit interface:
   ```bash
   python -m chainlit run src/interface/chainlit/app.py --watch
   ```

   Upload images or audio via the sidebar, or simply type messages into the chat interface to begin interacting with the AI Companion.

   ## 📌 Notes
   - WhatsApp integration requires:

      - API setup

      - ngrok tunnel for local exposure

   - Ensure all environment variables are configured properly

   ## License

   This project is open-source. Please check the repository for further details.
