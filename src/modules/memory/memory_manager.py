from src.modules.memory.vector_store import  get_vector_store
from src.models.analyze_memory_model import MemoryAnalysis
from src.prompts.analyze_memory_prompt import MEMORY_ANALYSIS_PROMPT
from src.llm.llm_provider import get_llm_provider
from datetime import datetime
from langchain_core.messages import BaseMessage
from typing import List



class MemoryManager:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.SIMILARITY_THRESHOLD = 0.5

    
    async def _analyze_memory(self, text: str) -> dict:
        """Analyzes the text to determine if it contains memory-worthy content.

        Args:
            text: The text content to analyze
        """
        prompt = MEMORY_ANALYSIS_PROMPT.format(message=text)
        llm = get_llm_provider()
        llm=llm.with_structured_output(MemoryAnalysis)
        response = await llm.ainvoke(prompt)
        return response
     
            


    async def extract_and_store_memory(self, message: BaseMessage):
        """
        Extracts memory from a message and stores it in the vector store.
        """
        if message.type != "human":
            return  # Only analyze human messages
        

        analysis = await self._analyze_memory(message.content)
        if analysis.is_important and analysis.formatted_memory:
            # Check if similar memory exists
            # similar = self.vector_store.find_similar_memory(analysis.formatted_memory)
            # if similar and similar.score > 0.7:  # Threshold for similarity
            #     print("Similar memory already exists, skipping storage.")
            #     return
            # Store the new memory
            self.vector_store.store_memory(analysis.formatted_memory, {"timestamp": datetime.now().isoformat(), "type": "extracted_memory"})

    
    def get_relevant_memories(self, context: str):
        """
        Retrieves relevant memories based on the given context.
        """
        memories = self.vector_store.search_memories(context, k=5)

        if memories:
            print(f"Retrieved {len(memories)} relevant memories.")
        
        # for memory in memories:
        #     print(f"Memory: {memory.text}, Score: {memory.score}")
        print(memories)
        return [memory.text for memory in memories if memory.score and memory.score >= self.SIMILARITY_THRESHOLD]  # Filter by relevance score

    def format_memories_for_prompt(self, memories: List[str]) -> str:
        """Format retrieved memories as bullet points."""
        print("Formatting memories for prompt:", memories)
        if not memories:
            return ""
        
        return "\n".join(f"- {memory}" for memory in memories)
    




def get_memory_manager() -> MemoryManager:
    """Factory function to get a singleton instance of MemoryManager."""
    return MemoryManager()

# if __name__ == "__main__":
#     memory_manager = get_memory_manager()
#     # Example usage
#     from langchain_core.messages import HumanMessage

#     # test_message = HumanMessage(content="I am a software developer who loves coding and learning new technologies.I work in meril life science and works as AI engineer.")
#     text_message = HumanMessage(content="I an aI engineer")
#     memory_manager.extract_and_store_memory(text_message)

#     context = "who am i?"
#     relevant_memories = memory_manager.get_relevant_memories(context)
#     print(memory_manager.format_memories_for_prompt(relevant_memories))

# python -m src.modules.memory.memory_manager