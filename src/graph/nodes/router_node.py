from src.graph.state import AgentState

from src.chains.router_chain import get_router_chain


async def router_node(state: AgentState) -> AgentState:
    router_chain = get_router_chain()

    messages_to_analyze = state["messages"][-3:]

    router_response = await router_chain.ainvoke({
        "messages": messages_to_analyze
    })

    return {"workflow": router_response.response_type}