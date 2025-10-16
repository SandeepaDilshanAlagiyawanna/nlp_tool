from audio_transcriber import AudioTranscriber
import os

def transcribe(audio_file_path):
    try:
        transcriber = AudioTranscriber("vosk-model-small-en-us-0.15")
        result = transcriber.transcribe_audio(audio_file_path, keep_converted=False)
        
        if result:
            return result['full_text']
        else:
            return None
            
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

if __name__ == "__main__":
    
    audio_file = "audios/hh.wav"
    
    print("Transcribing audio...")
    transcriber = AudioTranscriber("vosk-model-small-en-us-0.15")
    result = transcriber.transcribe_audio(audio_file, keep_converted=False)
    
    if result:
        print("Transcription: ")
        print(result['full_text'])
        
        audio_filename = os.path.basename(audio_file)
        output_filename = f"{os.path.splitext(audio_filename)[0]}_transcription.txt"
        transcriber.save_transcription(result, output_filename)
        print(f"✓ Transcription saved successfully!")
    else:
        print("Transcription failed!")