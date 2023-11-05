import pyaudio
import wave
import threading
import whisper
import pyautogui
from flask import Flask


class AudioRecorder:
    def __init__(
        self,
        chunk=1024,
        sample_format=pyaudio.paInt16,
        channels=1,
        fs=44100,
        filename="output.wav",
    ):
        self.chunk = chunk
        self.sample_format = sample_format
        self.channels = channels
        self.fs = fs
        self.filename = filename
        self.frames = []
        self.recording = False
        self.model = whisper.load_model("base")
        self.p = pyaudio.PyAudio()

    def start(self):
        self.recording = True
        print("Recording")
        self.frames = []  # Clear previous recording frames
        threading.Thread(target=self.record).start()

    def stop(self):
        self.recording = False
        print("Stopped recording")

    def record(self):
        stream = self.p.open(
            format=self.sample_format,
            channels=self.channels,
            rate=self.fs,
            frames_per_buffer=self.chunk,
            input=True,
        )
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        stream.stop_stream()
        stream.close()
        self.save_audio()

    def transcribe_recording(self):
        result = self.model.transcribe(self.filename)
        return result["text"]

    def save_audio(self):
        with wave.open(self.filename, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b"".join(self.frames))

        transcription = self.transcribe_recording()
        transcription = transcription.strip()

        print(f"Transcription: {transcription}")
        pyautogui.write(transcription)


def main():
    recorder = AudioRecorder()
    app = Flask(__name__)

    @app.post("/start")
    def start():
        recorder.start()
        return "Recording"

    @app.post("/stop")
    def stop():
        recorder.stop()
        return "Stopped"

    app.run()


if __name__ == "__main__":
    main()
