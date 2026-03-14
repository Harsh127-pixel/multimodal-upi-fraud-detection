import whisper

model = whisper.load_model("base")

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)

    return {
        "transcript": result["text"],
        "language": result["language"]
    }