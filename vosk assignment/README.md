# Audio Transcription with Vosk

A Python-based audio transcription system that converts speech in audio files to text using the Vosk speech recognition library. This project provides both a reusable class and command-line interface for transcribing MP3, WAV, and other audio formats.

## 🚀 Features

- **Multi-format Support**: Handles MP3, WAV, and other audio formats automatically
- **Automatic Audio Processing**: Converts audio to Vosk-compatible format (16kHz, mono, 16-bit WAV)
- **Word-level Timestamps**: Provides timing information for each recognized word
- **Real-time Processing**: Shows partial transcription results during processing
- **Organized Output**: Automatically saves transcriptions in a dedicated folder
- **Error Handling**: Comprehensive error checking and user-friendly messages
- **Virtual Environment Ready**: Pre-configured Python virtual environment included

## 📁 Project Structure

```
vosk assignment/
├── audio_transcriber.py      # Main transcription class with full functionality
├── main.py                   # Simple usage example and main entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This documentation
├── audios/                   # Sample audio files
│   ├── hh.wav               # Sample WAV file
│   └── jfk.mp3              # Sample MP3 file
├── transcriptions/           # Output directory for transcribed text
│   ├── hh_transcription.txt
│   └── jfk_transcription.txt
├── vosk-model-small-en-us-0.15/  # Pre-trained English speech model
└── env/                      # Python virtual environment (pre-configured)
    └── ...
```

## 🛠️ Setup

### Prerequisites
- Python 3.7+
- Windows (cmd.exe shell)
- Virtual environment (already configured in `env/`)

### Quick Start
1. **Activate the virtual environment**:
   ```cmd
   env\Scripts\activate
   ```

2. **Install dependencies** (if not already installed):
   ```cmd
   pip install -r requirements.txt
   ```

3. **Test with sample audio**:
   ```cmd
   python main.py
   ```

### Dependencies
- `vosk` - Offline speech recognition library
- `numpy` - Numerical computing (Vosk dependency)
- `pydub` - Audio file processing and format conversion

## 📖 Usage

### 1. Simple Usage (main.py)
The easiest way to get started:

```cmd
python main.py
```

This will transcribe the default audio file (`audios/hh.wav`) and display the result.

### 2. Using the AudioTranscriber Class

```python
from audio_transcriber import AudioTranscriber

# Initialize with default model
transcriber = AudioTranscriber()

# Transcribe an audio file
result = transcriber.transcribe_audio("audios/jfk.mp3")

if result:
    print("Transcription:", result['full_text'])
    
    # Save to transcriptions folder
    transcriber.save_transcription(result, "my_transcription.txt")
```

### 3. Advanced Usage with Timestamps

```python
from audio_transcriber import AudioTranscriber

transcriber = AudioTranscriber("vosk-model-small-en-us-0.15")
result = transcriber.transcribe_audio("your_audio.wav", keep_converted=True)

if result and 'detailed_results' in result:
    print("Full Text:", result['full_text'])
    print("\nDetailed Results:")
    
    for i, segment in enumerate(result['detailed_results'], 1):
        if 'text' in segment:
            print(f"Segment {i}: {segment['text']}")
            
            # Show word-level timestamps if available
            if 'result' in segment:
                for word_info in segment['result']:
                    word = word_info.get('word', '')
                    start = word_info.get('start', 0)
                    end = word_info.get('end', 0)
                    confidence = word_info.get('conf', 0)
                    print(f"  {word}: {start:.2f}s-{end:.2f}s (confidence: {confidence:.2f})")
```

### 4. Batch Processing Multiple Files

```python
from audio_transcriber import AudioTranscriber
import os

transcriber = AudioTranscriber()
audio_dir = "audios"

for filename in os.listdir(audio_dir):
    if filename.endswith(('.mp3', '.wav', '.m4a')):
        audio_path = os.path.join(audio_dir, filename)
        print(f"\nProcessing: {filename}")
        
        result = transcriber.transcribe_audio(audio_path)
        if result:
            output_name = f"{os.path.splitext(filename)[0]}_transcription.txt"
            transcriber.save_transcription(result, output_name)
            print(f"Saved: {output_name}")
```

## 🎯 Supported Audio Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| WAV | `.wav` | Native format, fastest processing |
| MP3 | `.mp3` | Automatically converted to WAV |
| M4A | `.m4a` | Supported via pydub |
| FLAC | `.flac` | Supported via pydub |
| OGG | `.ogg` | Supported via pydub |

**Note**: All formats are automatically converted to Vosk's required format (16kHz, mono, 16-bit WAV) during processing.

## 📊 Example Output

### Console Output:
```
Loading Vosk model from: vosk-model-small-en-us-0.15
Model loaded successfully!
Converting jfk.mp3 to WAV format...
Conversion completed: jfk_converted.wav
Transcribing: jfk_converted.wav
Processing audio...
Partial: my fellow americans
Partial: ask not what your country
Final: can do for you ask what you can do for your country
Transcription saved to: transcriptions/jfk_transcription.txt
Cleaned up temporary file: jfk_converted.wav
```

### Sample Transcription File:
```
my fellow americans ask not what your country can do for you ask what you can do for your country
```

## ⚙️ Configuration

### AudioTranscriber Class Parameters

```python
transcriber = AudioTranscriber(
    model_path="vosk-model-small-en-us-0.15"  # Path to Vosk model
)
```

### Method Parameters

```python
result = transcriber.transcribe_audio(
    audio_file,           # Path to audio file
    keep_converted=False  # Keep temporary WAV file after processing
)
```

## 🔧 Troubleshooting

### Common Issues

1. **"Model path does not exist"**
   ```
   Solution: Ensure vosk-model-small-en-us-0.15/ directory exists
   Download from: https://alphacephei.com/vosk/models
   ```

2. **"Error converting audio file"**
   ```
   Solution: Make sure pydub is installed: pip install pydub
   For MP3 support on Windows, pydub should work out of the box
   ```

3. **Virtual environment issues**
   ```
   Solution: 
   - Activate: env\Scripts\activate
   - Verify Python: python --version
   - Reinstall packages: pip install -r requirements.txt
   ```

4. **ImportError for vosk**
   ```
   Solution:
   - Activate virtual environment first
   - Install: pip install vosk
   - Check installation: python -c "import vosk; print('OK')"
   ```

### Performance Tips

- **File Size**: Longer files take more time (roughly real-time processing speed)
- **Format**: WAV files process faster (no conversion needed)
- **Quality**: Higher quality audio = better transcription accuracy
- **Model Size**: Small model (~40MB) for speed, larger models for accuracy

## 🎛️ Model Information

**Current Model**: `vosk-model-small-en-us-0.15`
- **Language**: English (US)
- **Size**: ~40MB
- **Accuracy**: Good for clear speech
- **Speed**: Fast processing
- **Use Case**: General purpose, podcasts, interviews

### Alternative Models
For better accuracy or other languages, download from [Vosk Models](https://alphacephei.com/vosk/models):

- `vosk-model-en-us-0.22` (1.8GB) - High accuracy English
- `vosk-model-small-de-0.15` (40MB) - German
- `vosk-model-small-fr-0.22` (40MB) - French
- `vosk-model-small-es-0.42` (40MB) - Spanish

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample audio files
5. Submit a pull request

## 📄 License

This project is open source. The Vosk library and models have their own licenses - please refer to the [Vosk documentation](https://github.com/alphacep/vosk-api) for details.

## 🔗 Resources

- [Vosk Official Website](https://alphacephei.com/vosk/)
- [Vosk GitHub Repository](https://github.com/alphacep/vosk-api)
- [Vosk Models Download](https://alphacephei.com/vosk/models)
- [Pydub Documentation](https://pydub.com/)