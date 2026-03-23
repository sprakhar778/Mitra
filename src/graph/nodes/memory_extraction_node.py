from src.graph.state import AgentState

from src.modules.memory.memory_manager import get_memory_manager


async def memory_extraction_node(state: AgentState) -> AgentState:
    """
    Node to extract memory context from the conversation 
    """
    # Implementation for extracting memory context and updating the state goes here
    memory_manager = get_memory_manager()

    # Extract the most recent messages to analyze for memory retrieval
    await memory_manager.extract_and_store_memory(state["messages"][-1])

    return {}




     