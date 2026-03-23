import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.prompts.character_prompt import CHARACTER_CARD_PROMPT
from src.llm.llm_provider import get_llm_provider






def remove_asterisk_content(text: str) -> str:
    """Remove content between asterisks from the text."""
    return re.sub(r"\*.*?\*", "", text).strip()


class AsteriskRemovalParser(StrOutputParser):
    def parse(self, text):
        return remove_asterisk_content(super().parse(text))



def get_character_response_chain(summary: str = ""):
    model = get_llm_provider()
    system_message = CHARACTER_CARD_PROMPT

    if summary:
        system_message += f"\n\nSummary of conversation earlier between Ava and the user: {summary}"

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("system","{memory_context}"),
            MessagesPlaceholder(variable_name="messages"),
            
        ]
    )

    return prompt | model | AsteriskRemovalParser()

# if __name__ == "__main__":
#     # Example usage
#     chain = get_character_response_chain(summary="The user and Ava had a conversation about their favorite movies. The user mentioned they love sci-fi movies, especially 'Interstellar'. Ava shared that she enjoys romantic comedies and recently watched 'Crazy Rich Asians'.")
#     example_messages = [
#         {"role": "user", "content": "Hi Ava! How are you today?"},
#         {"role": "assistant", "content": "Hello! I'm doing great, thank you for asking. How can I assist you today?"},
#     ]
#     response = chain.invoke(example_messages)
#     print(response)

#python -m src.chains.character_chain