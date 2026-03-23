from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.prompts.router_prompt import ROUTER_PROMPT
from src.llm.llm_provider import get_llm_provider


class RouterResponse(BaseModel):
    response_type: str = Field(
        description="The response type to give to the user. It must be one of: 'conversation', 'image' or 'audio'"
    )


def get_router_chain():
    model = get_llm_provider().with_structured_output(RouterResponse)

    prompt = ChatPromptTemplate.from_messages(
        [("system", ROUTER_PROMPT), MessagesPlaceholder(variable_name="messages")]
    )

    return prompt | model


# if __name__ == "__main__":
#     # Example usage
#     chain = get_router_chain()
#     example_messages = [
#         {"role": "user", "content": "Can you show me a picture of a cat?"},
#         {"role": "assistant", "content": "Sure! Here's a cute cat picture."},
#     ]
#     response = chain.invoke(example_messages)
#     print(response.response_type)

#python -m src.chains.router_chain