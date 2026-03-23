from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """State class for the AI Companion workflow.

    Extends MessagesState to track conversation history and maintains the last message received.

    Attributes:
        last_message (AnyMessage): The most recent message in the conversation, can be any valid
            LangChain message type (HumanMessage, AIMessage, etc.)
        workflow (str): The current workflow the AI Companion is in. Can be "conversation", "image", or "audio".
        audio_buffer (bytes): The audio buffer to be used for speech-to-text conversion.
        image_path (str): The file path to the most recently received image, if any.
        memory_context (str): The context of the memories to be injected into the character card.
    """

    summary: str
    workflow: str
    audio_buffer: bytes
    image_path: str
   
    memory_context: str
