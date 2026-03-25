from src.graph.state import AgentState
from langchain_core.messages import HumanMessage, RemoveMessage
from src.llm.llm_provider import get_llm_provider
from src.core.settings import settings



async def summarize_conversation_node(state: AgentState):
    model = get_llm_provider()
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is summary of the conversation to date between Ava and the user: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = (
            "Create a summary of the conversation above between Ava and the user. "
            "The summary must be a short description of the conversation so far, "
            "but that captures all the relevant information shared between Ava and the user:"
        )

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = await model.ainvoke(messages)
    #RemoveMessage is a special message type that tells the system to delete the message with the given id from the conversation history. We want to delete all messages except the most recent ones that we want to keep for context.
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][: -settings.TOTAL_MESSAGES_AFTER_SUMMARY]]
    return {"summary": response.content, "messages": delete_messages}
