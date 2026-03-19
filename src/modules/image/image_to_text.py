import base64
from email.mime import message
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage
from typing import Union ,List,Literal
from src.core.settings import settings
from src.core.exceptions import ImageToTextError

from dotenv import load_dotenv
load_dotenv()





class ImageToText:
    def __init__(self):
        
        self.llm = ChatGroq(model=settings.GROQ_IMAGE_MODEL_NAME)

    def _encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
        

    async def analyze_image(self, image:Union[str, bytes]) -> str:
        try:
            if isinstance(image, bytes):
                
                base64_image = base64.b64encode(image).decode('utf-8')
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": "Please describe what you see in this image in detail."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ]
                )
            elif isinstance(image, str):
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": "Please describe what you see in this image in detail."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self._encode_image(image)}"}},
                    ]
                )
            else:
                raise ValueError("Image must be a bytes object or a string URL.")
            

            try:
                response = await self.llm.ainvoke([message])
                return response.content
            
            except Exception as e:
                   raise ImageToTextError(f"Failed to get response from model: {str(e)}") from e  
                  
        except Exception as e:
            raise ImageToTextError(f"Failed to analyze image: {str(e)}") from e

    

# async def main():
#     print("Starting...")
#     image_to_text = ImageToText()
#     print("Initialized model")

#     description = await image_to_text.analyze_image("notebooks/data/rag.jpeg")
#     print("Got response:", description)

# import asyncio

# if __name__ == "__main__":
#     asyncio.run(main())