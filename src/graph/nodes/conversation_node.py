from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig
from src.graph.state import AgentState
from src.chains.character_chain import get_character_response_chain





async def conversation_node(state: AgentState, config: RunnableConfig):
 
   
    chain = get_character_response_chain(state.get("summary", ""))
    memory_context = state.get("memory_context", "")
    response = await chain.ainvoke(
        {
            "messages": state["messages"],
            
            "memory_context": memory_context,
        },
        config,
    )
    return {"messages": AIMessage(content=response)}
