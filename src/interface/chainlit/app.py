import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from io import BytesIO
import base64
import chainlit as cl
from PIL import Image
from src.core.settings import settings

from langchain_core.messages import AIMessageChunk,HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.modules.image.image_to_text import get_image_to_text_module
from src.modules.speech.speech_to_text import get_speech_to_text_module
from src.modules.speech.text_to_speech import get_text_to_speech_module
from src.graph.graph import create_workflow_graph



image_to_text_module = get_image_to_text_module()
speech_to_text_module = get_speech_to_text_module()
text_to_speech_module = get_text_to_speech_module()

@cl.on_chat_start
async def on_chat_start():
     cl.user_session.set("thread_id", 1)


@cl.on_message
async def on_message(message:cl.Message):
    """
    Handle Text and Images
    """
    #empty message
    msg=cl.Message(content="")

    content=message.content
    
    if message.elements:
         for element in message.elements:
            if isinstance(element, cl.Audio):
                with open(element.path, "rb") as f:
                    audio_data = f.read()

                # mime_type = element.mime

                # print("📁 AUDIO FILE RECEIVED:", element.path)
                # print("MIME:", mime_type)
                # print("SIZE:", len(audio_data))
                # input_audio_el = cl.Audio(mime=mime_type, content=audio_data)
                # #audio message
                # await cl.Message(author="You", content="", elements=[input_audio_el]).send()

                transcription = await speech_to_text_module.transcribe(audio_data)

                
                # show transcription
                await cl.Message(content=f"📝 Transcription: {transcription}").send()

                content+=f"\n\n{transcription}"
                thread_id = cl.user_session.get("thread_id")
                async with cl.Step(type="run"):
                    async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
                        graph = create_workflow_graph().compile(checkpointer=short_term_memory)
                        output_state = await graph.ainvoke(
                            {"messages": [HumanMessage(content=content)]},
                            {"configurable": {"thread_id": thread_id}},
                        )

                # Use global TextToSpeech instance
                audio_buffer = await text_to_speech_module.synthesize(output_state["messages"][-1].content)

                output_audio_el = cl.Audio(
                    name="Audio",
                    auto_play=True,
                    mime="audio/mpeg3",
                    content=audio_buffer,
                )
                await cl.Message(content=output_state["messages"][-1].content, elements=[output_audio_el]).send()
                return



               


               
            #handle image
            if isinstance(element, cl.Image):
                with open(element.path, "rb") as f:
                    image_bytes = f.read()
                
                try:
                    #analyze image and add content to message
                    image_text = await image_to_text_module.analyze_image(image_bytes)
                    content+=f"\n\nImage Description: {image_text}"
                except Exception as e:
                    content+=f"\n\nImage Description: Error analyzing image - {e}"
    
    thread_id = cl.user_session.get("thread_id")

    async with cl.Step(type="run"):
        async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as short_term_memory:
            graph = create_workflow_graph().compile(checkpointer=short_term_memory)
            async for chunk in graph.astream(
                {"messages": [HumanMessage(content=content)]},
                {"configurable": {"thread_id": thread_id}},
                stream_mode="messages",
            ):
                if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(chunk[0], AIMessageChunk):
                    await msg.stream_token(chunk[0].content)

            output_state = await graph.aget_state(config={"configurable": {"thread_id": thread_id}})
    
    if output_state.values.get("workflow")=="audio":
        #but i want last human message as response not the audio response message
        response = output_state.values.get("messages")[-1].content
        
        # to remove the prefix "Audio response generated based on the prompt: " from the response
        response = response.split(":", 1)[-1].strip()

        audio_bytes = output_state.values.get("audio_buffer")

        output_audio_el = cl.Audio(
            name="Audio",
            auto_play=True,
            mime="audio/mpeg3",
            content=audio_bytes,
        )
        await cl.Message(content=response, elements=[output_audio_el]).send()

    elif output_state.values.get("workflow") == "image":
        # response = output_state.values["messages"][-1].content
        response =""
        image = cl.Image(path=output_state.values["image_path"], display="inline")
        await cl.Message(content=response, elements=[image]).send()
    else:
        await msg.send()


