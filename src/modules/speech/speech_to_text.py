import os
import tempfile
from groq import Groq

from src.core.settings import settings
from src.core.exceptions import SpeechToTextError


class SpeechToText:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def transcribe(self, audio_data: bytes) -> str:
        if not audio_data:
            raise ValueError("Audio data cannot be empty")

        temp_path = None

        try:
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            # Send to Groq
            with open(temp_path, "rb") as f:
                result = self.client.audio.transcriptions.create(
                    file=f,
                    model="whisper-large-v3-turbo",
                    language="en",
                    response_format="text",
                )

            if not result:
                raise SpeechToTextError("Empty transcription")

            return result

        except Exception as e:
            raise SpeechToTextError(f"Failed: {e}") from e

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

def get_speech_to_text_module():
    return SpeechToText()

# if __name__ == "__main__":
#     import asyncio

#     async def main():
      
#         speech_to_text = SpeechToText()
      
#         with open("output_audio.wav", "rb") as f:
#             audio_data = f.read()
#         transcription = await speech_to_text.transcribe(audio_data)
#         print("Transcription:", transcription)

#     asyncio.run(main())

# python -m src.modules.speech.speech_to_text