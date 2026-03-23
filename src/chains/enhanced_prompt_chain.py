from src.llm.llm_provider import get_llm_provider
from src.prompts.image_enhanced_prompt import IMAGE_ENHANCEMENT_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel ,Field

class ImageEnhancementResponse(BaseModel):
    enhanced_prompt: str=Field(description="The enhanced prompt that captures the intent behind the original user message and is used by image generation models to create images that align with the user's request.")

async def enhanced_prompt_chain(user_message: str, memory_context: str) -> str:
    model = get_llm_provider()

    prompt = ChatPromptTemplate.from_messages(
        [("system", IMAGE_ENHANCEMENT_PROMPT), ("user", "{user_message}"), ("system", "{memory_context}")]
    )
    chain= prompt | model.with_structured_output(ImageEnhancementResponse) | (lambda x: x.enhanced_prompt)
    
    res=await chain.ainvoke ({"user_message": user_message, "memory_context": memory_context})
    return res