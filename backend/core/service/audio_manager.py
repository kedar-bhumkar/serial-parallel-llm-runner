import base64
from openai import OpenAI
from backend.core.utility.constants import *
from backend.core.utility.util import getConfig


config = getConfig(config_file)
model_family = "groq"
client = OpenAI(api_key  = config[model_family]["key"],base_url = config[model_family]["url"])


def transcribe(data):
    print('Inside transcribe')
    audio_base64 = data
    audio_bytes = base64.b64decode(audio_base64)

    # Save the received audio file as WebM locally
    webm_filename = 'received_audio.webm'
    with open(webm_filename, 'wb') as audio_file:
        audio_file.write(audio_bytes)

    transcription = doAudioTranscription(webm_filename)
    return {"transcription": transcription.text}

def doAudioTranscription(filename):

    audio_file= open(filename, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-large-v3", 
    file=audio_file,
    language="en",
    temperature=0
    )

    print(transcription.text)

    return transcription


#doAudioTranscription("aaji.m4a")