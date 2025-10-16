import json
import os
import sys
import wave
from pydub import AudioSegment
import vosk


class AudioTranscriber:
    def __init__(self, model_path="vosk-model-small-en-us-0.15"):
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        if not os.path.exists(self.model_path):
            print(f"Error: Model path '{self.model_path}' does not exist!")
            print("Please download a Vosk model from https://alphacephei.com/vosk/models")
            sys.exit(1)
        
        print(f"Loading Vosk model from: {self.model_path}")
        self.model = vosk.Model(self.model_path)
        print("Model loaded successfully!")
    
    def convert_to_wav(self, input_file, output_file=None):
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_converted.wav"
        
        print(f"Converting {input_file} to WAV format...")
        
        try:
            audio = AudioSegment.from_file(input_file)
            # Convert to mono and set sample rate to 16kHz (Vosk requirement)
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(16000)  # 16kHz sample rate
            audio = audio.set_sample_width(2)  # 16-bit
            
            audio.export(output_file, format="wav")
            print(f"Conversion completed: {output_file}")
            
            return output_file
            
        except Exception as e:
            print(f"Error converting audio file: {e}")
            return None
    
    def transcribe_wav(self, wav_file):
        if not os.path.exists(wav_file):
            print(f"Error: WAV file '{wav_file}' does not exist!")
            return None
        
        print(f"Transcribing: {wav_file}")
        
        try:
            wf = wave.open(wav_file, 'rb')
            
            # Check if WAV file is compatible
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
                print("Error: WAV file must be mono, 16-bit PCM format")
                wf.close()
                return None
            
            # Create recognizer
            rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)  # Enable word-level timestamps
            
            transcription = []
            full_text = ""
            
            print("Processing audio...")
            
            # Process audio in chunks
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get('text'):
                        transcription.append(result)
                        full_text += result['text'] + " "
                        print(f"Partial: {result['text']}")
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                transcription.append(final_result)
                full_text += final_result['text']
                print(f"Final: {final_result['text']}")
            
            wf.close()
            
            return {
                'full_text': full_text.strip(),
                'detailed_results': transcription
            }
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
    
    def transcribe_audio(self, audio_file, keep_converted=False):
        if not os.path.exists(audio_file):
            print(f"Error: Audio file '{audio_file}' does not exist!")
            return None
        
        file_extension = os.path.splitext(audio_file)[1].lower()
        
        if file_extension == '.wav':
            try:
                wf = wave.open(audio_file, 'rb')
                is_correct_format = (wf.getnchannels() == 1 and 
                                   wf.getsampwidth() == 2 and 
                                   wf.getcomptype() == 'NONE' and
                                   wf.getframerate() == 16000)
                wf.close()
                
                if is_correct_format:
                    return self.transcribe_wav(audio_file)
                else:
                    print("WAV file is not in correct format (mono, 16-bit, 16kHz). Converting...")
            except Exception as e:
                print(f"Error checking WAV format: {e}. Converting...")

        wav_file = self.convert_to_wav(audio_file)
        if wav_file is None:
            return None
        
        result = self.transcribe_wav(wav_file)
        
        if not keep_converted and os.path.exists(wav_file) and wav_file != audio_file:
            os.remove(wav_file)
            print(f"Cleaned up temporary file: {wav_file}")
        
        return result
    
    def save_transcription(self, transcription, output_file):
        try:
            transcriptions_dir = "transcriptions"
            if not os.path.exists(transcriptions_dir):
                os.makedirs(transcriptions_dir)
                print(f"Created directory: {transcriptions_dir}")
            
            filename = os.path.basename(output_file)
            full_output_path = os.path.join(transcriptions_dir, filename)
            
            with open(full_output_path, 'w', encoding='utf-8') as f:
                f.write(transcription['full_text'])
            
            print(f"Transcription saved to: {full_output_path}")
            
        except Exception as e:
            print(f"Error saving transcription: {e}")
