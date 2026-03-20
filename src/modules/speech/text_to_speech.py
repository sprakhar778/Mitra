

from src.core.settings import settings
from src.core.exceptions import TextToSpeechError
from deepgram import DeepgramClient


class TextToSpeech:
    def __init__(self):
        self.client = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)

    async def synthesize(self, text: str) -> bytes:
        try:
            response = self.client.speak.v1.audio.generate(
                text=text,
                model=settings.DEEPGRAM_SPEECH_MODEL_NAME,
            )

            # In new SDK, audio is returned as bytes directly
            audio_bytes = b"".join(response)

            if not audio_bytes:
                raise TextToSpeechError("Generated audio is empty")

            return audio_bytes

        except Exception as e:
            raise TextToSpeechError(f"TTS failed: {str(e)}") from e
        





# if __name__ == "__main__":
#     import asyncio

#     async def main():
#         text_to_speech = TextToSpeech()
#         text = "Hello, this is a test of the text-to-speech functionality."
#         audio_data = await text_to_speech.synthesize(text)
#         with open("output_audio.wav", "wb") as f:
#             f.write(audio_data)
#         print("Audio synthesized and saved to output_audio.wav")

#     asyncio.run(main())

# python -m src.modules.speech.text_to_speech