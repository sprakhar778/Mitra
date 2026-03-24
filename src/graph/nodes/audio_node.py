from langchain_core.runnables import RunnableConfig
from src.graph.state import AgentState
from src.modules.speech.speech_to_text import get_speech_to_text_module
from src.modules.speech.text_to_speech import get_text_to_speech_module
from langchain_core.messages import AIMessage
from src.chains.character_chain import get_character_response_chain


async def audio_node(state: AgentState, config: RunnableConfig):
    """
    Node to handle audio input and output.
    """
    chain=get_character_response_chain(state.get("summary", ""))
   
    text_to_speech_module = get_text_to_speech_module()

    response=await chain.ainvoke(
        {
            "messages": state["messages"],
            "memory_context": state.get("memory_context", ""),
        },
        config,
    )

    audio_buffer = await text_to_speech_module.synthesize(response)
   
    
    return {"response": response, "audio_buffer": audio_buffer,"messages": AIMessage(content=f"Audio response generated based on the prompt: {response}")}