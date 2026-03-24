from src.modules.image.text_to_image import get_text_to_image_module
from src.graph.state import AgentState
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from src.chains.enhanced_prompt_chain import enhanced_prompt_chain
import uuid
import os


async def image_node(state: AgentState, config: RunnableConfig):
    """
    Node to handle image generation requests.
    """
    text_to_image_module = get_text_to_image_module()

    # Extract the last 3 messages to use as the prompt for image generation
    if len(state["messages"]) < 3:
        conversation_context = "\n".join([msg.content for msg in state["messages"]])  # All messages if less than 3
    else:
        conversation_context = "\n".join([msg.content for msg in state["messages"][-3:]])  # Last 3 messages

    prompt = conversation_context

    enhanced_prompt = await enhanced_prompt_chain(prompt,memory_context=state.get("memory_context", ""))
    os.makedirs("generated_images", exist_ok=True)
    img_path = f"generated_images/image_{str(uuid.uuid4())}.png"
    try:
        image_path = await text_to_image_module.generate_image(enhanced_prompt,output_path=img_path)
        return {"image_path": image_path,"messages": AIMessage(content=f"Image generated based on the prompt: {enhanced_prompt}")}
    except Exception as e:
        return {"error": f"Failed to generate image: {str(e)}"}