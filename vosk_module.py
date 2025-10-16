"""
Vosk Speech-to-Text Module
Transcribes audio files to English text using Vosk model
"""

import json
import os
import wave
from pydub import AudioSegment
import vosk


def transcribe_audio(
    audio_file_path, model_path="vosk assignment/vosk-model-small-en-us-0.15"
):
    """
    Transcribe audio file to text using Vosk

    Args:
        audio_file_path: Path to the audio file
        model_path: Path to the Vosk model directory

    Returns:
        str: Transcribed text or None if failed
    """
    try:
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"Error: Model path '{model_path}' does not exist!")
            return None

        # Load Vosk model
        print(f"Loading Vosk model from: {model_path}")
        model = vosk.Model(model_path)
        print("Model loaded successfully!")

        # Convert to WAV if needed
        wav_file = audio_file_path
        temp_file = None

        if not audio_file_path.lower().endswith(".wav"):
            print(f"Converting {audio_file_path} to WAV format...")
            temp_file = audio_file_path + "_temp.wav"
            audio = AudioSegment.from_file(audio_file_path)
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(16000)  # 16kHz
            audio = audio.set_sample_width(2)  # 16-bit
            audio.export(temp_file, format="wav")
            wav_file = temp_file
            print(f"Conversion completed: {wav_file}")

        # Transcribe
        print(f"Transcribing: {wav_file}")
        wf = wave.open(wav_file, "rb")

        # Check WAV format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            print("Converting WAV to correct format...")
            wf.close()
            temp_file = audio_file_path + "_temp.wav"
            audio = AudioSegment.from_file(wav_file)
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            audio = audio.set_sample_width(2)
            audio.export(temp_file, format="wav")
            wf = wave.open(temp_file, "rb")

        # Create recognizer
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        full_text = ""
        print("Processing audio...")

        # Process audio in chunks
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get("text"):
                    full_text += result["text"] + " "

        # Get final result
        final_result = json.loads(rec.FinalResult())
        if final_result.get("text"):
            full_text += final_result["text"]

        wf.close()

        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"Cleaned up temporary file: {temp_file}")

        transcription = full_text.strip()
        print(f"Transcription completed: {transcription[:100]}...")
        return transcription

    except Exception as e:
        print(f"Error during transcription: {e}")
        # Clean up temporary file on error
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
        return None


if __name__ == "__main__":
    # Test the module
    test_audio = "vosk assignment/audios/hh.wav"
    if os.path.exists(test_audio):
        result = transcribe_audio(test_audio)
        print(f"\nTranscription: {result}")
    else:
        print(f"Test file not found: {test_audio}")
