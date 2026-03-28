import base64
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage
from typing import Union ,List,Literal
from src.core.settings import settings
from src.core.exceptions import ImageToTextError
import imghdr
from dotenv import load_dotenv
load_dotenv()


class ImageToText:
    def __init__(self):
        self.llm = ChatGroq(model=settings.GROQ_IMAGE_MODEL_NAME)

    def _encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_mime_type(self, image_bytes):
        t = imghdr.what(None, h=image_bytes)
        return f"image/{t or 'jpeg'}"

    async def analyze_image(self, image: Union[str, bytes], user_request: str = "") -> str:
        try:
            text_content = user_request or "Please describe what you see in this image in detail."

            # --- Handle image input ---
            if isinstance(image, bytes):
                image_bytes = image

            elif isinstance(image, str):
                with open(image, "rb") as f:
                    image_bytes = f.read()

            else:
                raise ValueError("Image must be a bytes object or a file path.")

            # --- Encode ---
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            mime = self.get_mime_type(image_bytes)

            print("Mime",mime)

            message = HumanMessage(
                content=[
                    {"type": "text", "text": text_content},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}},
                ]
            )

            # --- Call model ---
            response = await self.llm.ainvoke([message])
            return response.content

        except Exception as e:
            raise ImageToTextError(f"Failed to analyze image: {str(e)}") from e


def get_image_to_text_module():
    return ImageToText()


# async def main():
#     print("Starting...")
#     image_to_text = ImageToText()
#     print("Initialized model")

#     description = await image_to_text.analyze_image("notebooks/data/rag.jpeg")
#     print("Got response:", description)

# import asyncio

# if __name__ == "__main__":
#     asyncio.run(main())


# python -m src.modules.image.image_to_text