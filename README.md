# 🎙️ Integrated NLP Pipeline Application

A comprehensive NLP application that processes audio through a complete pipeline: **Speech-to-Text → Summarization → English-to-Sinhala Translation**

## 🌟 Features

1. **Speech-to-Text (Vosk)**: Convert English audio to text using the Vosk speech recognition model
2. **Text Summarization (TF-IDF)**: Automatically summarize the transcribed text using TF-IDF algorithm
3. **English-to-Sinhala Translation (MT5)**: Translate the summary to Sinhala using the MT5 model
4. **Modern Web UI**: Beautiful, interactive interface with drag-and-drop audio upload
5. **Real-time Progress**: Visual step-by-step progress indicator
6. **Multiple Audio Formats**: Supports WAV, MP3, M4A, OGG, and more

## 📁 Project Structure

```
NLP tool Development/
├── integrated_app.py           # Main FastAPI application
├── vosk_module.py              # Speech-to-Text module
├── summarizer_module.py        # Text summarization module
├── translator_module.py        # Translation module
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── uploads/                    # Temporary upload directory (auto-created)
└── vosk assignment/
    └── vosk-model-small-en-us-0.15/  # Vosk model directory
```

## 🚀 Installation

> **💡 No Docker Required!** This app runs directly with Python. Docker files are included only as an optional deployment method.

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio format conversion)


**That's it!** The script will automatically install everything and start the server.

### Manual Installation

**1. Install FFmpeg:**

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

**2. Install Python Dependencies:**

### Install Python Dependencies

```bash
# Navigate to the project directory
cd ""

# Install requirements
pip install -r requirements.txt
```

### Download NLTK Data

The application will automatically download required NLTK data on first run, but you can pre-download:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## 🎯 Usage

### Start the Application

```bash
python integrated_app.py
```

The server will start at: **http://localhost:8000**

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. **Upload Audio**:
   - Drag and drop an audio file onto the upload box, OR
   - Click the upload box to browse and select a file
3. **Process**: Click the "Process Audio" button
4. **View Results**:
   - Watch the progress through 3 steps
   - View the transcribed text
   - Read the summary
   - See the Sinhala translation

### Supported Audio Formats

- WAV (recommended)
- MP3
- M4A
- OGG
- FLAC
- And more (any format supported by pydub/ffmpeg)

## 🔧 API Endpoints

### `GET /`

Returns the web interface (HTML page)

### `POST /process-audio`

Process an audio file through the complete pipeline

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body: Audio file

**Response:**

```json
{
  "transcription": "Full transcribed text...",
  "summary": "Summarized version...",
  "translation": "සිංහල පරිවර්තනය...",
  "status": "success"
}
```

### `GET /health`

Health check endpoint

**Response:**

```json
{
  "status": "healthy",
  "message": "NLP Pipeline API is running"
}
```

## 📊 Pipeline Details

### 1. Speech-to-Text (Vosk)

- Model: `vosk-model-small-en-us-0.15`
- Automatically converts audio to required format (mono, 16kHz, 16-bit)
- Supports various audio formats through pydub

### 2. Text Summarization (TF-IDF)

- Implements TF-IDF (Term Frequency-Inverse Document Frequency) algorithm
- Extracts top 3 most important sentences
- Maintains original sentence order
- Removes stopwords for better accuracy

### 3. English-to-Sinhala Translation (MT5)

- Model: `thilina/mt5-sinhalese-english`
- Transformer-based neural machine translation
- Cached model for faster subsequent translations

## 🎨 UI Features

- **Modern Gradient Design**: Purple gradient background with smooth animations
- **Drag & Drop**: Easy file upload with visual feedback
- **Progress Indicators**: Step-by-step visual progress
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Clear error messages and status updates
- **Result Cards**: Well-organized display of all three outputs

## 🧪 Testing Individual Modules

### Test Speech-to-Text

```bash
python vosk_module.py
```

### Test Summarization

```bash
python summarizer_module.py
```

### Test Translation

```bash
python translator_module.py
```

## 🐛 Troubleshooting

### Model Not Found Error

Ensure the Vosk model is in the correct path:

```
vosk assignment/vosk-model-small-en-us-0.15/
```

### FFmpeg Error

Install FFmpeg as described in the installation section.

### Memory Issues with Translation

The MT5 model requires significant memory. Consider:

- Using a smaller model
- Processing shorter texts
- Increasing available RAM

### NLTK Data Not Found

Run:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## 📝 Development

### Running in Development Mode

```bash
uvicorn integrated_app:app --reload --host 0.0.0.0 --port 8000
```

### Customization

**Change summary length:**
Edit `integrated_app.py`, line in `process_audio()`:

```python
summary = summarize_text(transcription, num_sentences=5)  # Change from 3 to 5
```

**Change Vosk model:**
Edit `vosk_module.py`:

```python
def transcribe_audio(audio_file_path, model_path="path/to/your/model"):
```

## 📄 License

This project is part of CM3620 - Natural Language Processing course work.

## 👥 Contributors

L3S2 Group Project - NLP Tool Development

## 🙏 Acknowledgments

- **Vosk**: Speech recognition toolkit
- **NLTK**: Natural Language Toolkit
- **Hugging Face Transformers**: MT5 translation model
- **FastAPI**: Modern web framework

## 📧 Support

For issues and questions, please contact your course instructor or teaching assistants.

---

**Enjoy using the NLP Pipeline Application! 🚀**
