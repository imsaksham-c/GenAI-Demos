import os
from openai import OpenAI

def text_to_speech(text, filename="output_audio.wav"):
    client = OpenAI()
    print("starting audio gen")
    # Generate speech using OpenAI's TTS API
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",  # You can choose from: alloy, echo, fable, onyx, nova, shimmer
        input=text
    )
    
    # Save the audio file
    response.stream_to_file(filename)
    print("done audio gen")
    return filename
