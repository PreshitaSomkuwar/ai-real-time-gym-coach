from io import BytesIO
from gtts import gTTS


class TextToSpeech:
    def speak(self, text, lang="en"):
        cleaned = (text or "").strip()

        print("TTS TEXT:", repr(cleaned))

        if not cleaned:
            print("TTS TEXT IS EMPTY")
            return None

        try:
            buffer = BytesIO()
            gTTS(text=cleaned, lang=lang).write_to_fp(buffer)

            audio = buffer.getvalue()

            print("TTS BYTES:", len(audio))

            return audio

        except Exception as e:
            print("TTS ERROR:", repr(e))
            return None