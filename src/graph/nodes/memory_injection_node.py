from src.graph.state import AgentState

from src.modules.memory.memory_manager import get_memory_manager


async def memory_injection_node(state: AgentState) -> AgentState:
    """
    Node to inject relevant memories into the character card context.
    """
    memory_manager = get_memory_manager()

    # Get the current conversation context (e.g., last few messages)
    if len(state["messages"]) < 5:
        conversation_context = "\n".join([msg.content for msg in state["messages"]])  # All messages if less than 5
    else:
        conversation_context = "\n".join([msg.content for msg in state["messages"][-5:]])  # Last 5 messages

    # Retrieve relevant memories based on the conversation context
    relevant_memories = memory_manager.get_relevant_memories(conversation_context)

    # Format the retrieved memories for injection into the character card
    formatted_memory_context = memory_manager.format_memories_for_prompt(relevant_memories)
    # print(f"Formatted Memory Context:\n{formatted_memory_context}")

    return {"memory_context": formatted_memory_context}