# Quick Start Guide

## Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python integrated_app.py
```

## Access the Application

Open your browser and go to: **http://localhost:8000**

## Quick Test

1. Upload an audio file (WAV, MP3, etc.)
2. Click "Process Audio"
3. Wait for the pipeline to complete
4. View your results:
   - Transcribed text
   - Summary
   - Sinhala translation

## System Requirements

- Python 3.8+
- FFmpeg (for audio conversion)
- 4GB+ RAM (for MT5 translation model)
- Internet connection (first time to download models)

## Common Issues

**FFmpeg not installed:**

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

**NLTK data missing:**
The app will auto-download on first run, or manually:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

**Port 8000 already in use:**

```bash
# Change port in integrated_app.py (last line)
uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

For detailed documentation, see [README.md](README.md)
