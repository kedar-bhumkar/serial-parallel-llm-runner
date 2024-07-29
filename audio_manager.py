import base64
def transcribe(data):
    print('Inside transcribe')
    audio_base64 = data
    audio_bytes = base64.b64decode(audio_base64)

    # Save the received audio file as WebM locally
    webm_filename = 'received_audio.webm'
    with open(webm_filename, 'wb') as audio_file:
        audio_file.write(audio_bytes)

    return "success"