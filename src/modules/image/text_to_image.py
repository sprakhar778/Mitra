from src.core.settings import settings
from src.core.exceptions import TextToImageError
from google import genai
from google.genai import types
from PIL import Image
import os



class TextToImage:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    async def generate_image(self, prompt: str, output_path: str) -> Image.Image:
        try:
            response = self.client.models.generate_content(
            model=settings.IMAGE_GENERATION_MODEL_NAME,
                contents=[prompt],
            )

            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    image.save(output_path)
                    return image

            raise TextToImageError("No image data found in the response.")
        
        except Exception as e:
            raise TextToImageError(f"Failed to generate image: {str(e)}") from e
    

# if __name__ == "__main__":
#     import asyncio

#     async def main():
#         text_to_image = TextToImage()
#         prompt = "A serene landscape with mountains, a river, and a clear blue sky."
#         output_path = "generated_images/serene_landscape.png"
#         image = await text_to_image.generate_image(prompt, output_path)
#         print(f"Image generated and saved to {output_path}")

#     asyncio.run(main())

#python -m src.modules.image.text_to_image