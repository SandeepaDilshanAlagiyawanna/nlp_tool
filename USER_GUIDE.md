# 📖 User Guide - NLP Pipeline Application

## Table of Contents

1. [Getting Started](#getting-started)
2. [Using the Web Interface](#using-the-web-interface)
3. [API Usage](#api-usage)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Examples](#examples)

---

## Getting Started

### Installation

1. **Install FFmpeg** (required for audio processing):

   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # macOS
   brew install ffmpeg
   ```

2. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python test_modules.py
   ```

### Quick Start

**Option 1: Using the startup script**

```bash
./start.sh
```

**Option 2: Manual start**

```bash
python integrated_app.py
```

The application will be available at: **http://localhost:8000**

---

## Using the Web Interface

### Step-by-Step Guide

1. **Access the Application**

   - Open your web browser
   - Navigate to `http://localhost:8000`

2. **Upload Audio File**

   **Method A: Drag and Drop**

   - Drag your audio file from file explorer
   - Drop it onto the purple upload box

   **Method B: Browse**

   - Click on the upload box
   - Select your audio file from the file dialog

3. **Process Audio**

   - Click the "Process Audio" button
   - Wait for the pipeline to complete (3 steps)

4. **View Results**
   - **Transcription**: Original English text from audio
   - **Summary**: Condensed version (top 3 sentences)
   - **Translation**: Sinhala translation of the summary

### Supported Audio Formats

✅ **Supported:**

- WAV (recommended for best quality)
- MP3
- M4A
- OGG
- FLAC
- AAC
- WMA

⚠️ **Requirements:**

- File size: Up to 100MB
- Audio should be in English
- Clear audio produces better results

---

## API Usage

### Using cURL

**Process an audio file:**

```bash
curl -X POST "http://localhost:8000/process-audio" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/audio.wav"
```

**Response:**

```json
{
  "transcription": "This is the full transcribed text from the audio file...",
  "summary": "This is the condensed summary of the transcription...",
  "translation": "මෙය සාරාංශයේ සිංහල පරිවර්තනය වේ...",
  "status": "success"
}
```

### Using Python

```python
import requests

# Upload and process audio
url = "http://localhost:8000/process-audio"
files = {"file": open("audio.wav", "rb")}
response = requests.post(url, files=files)

result = response.json()
print("Transcription:", result["transcription"])
print("Summary:", result["summary"])
print("Translation:", result["translation"])
```

### Using JavaScript/Fetch

```javascript
const fileInput = document.getElementById("fileInput");
const file = fileInput.files[0];

const formData = new FormData();
formData.append("file", file);

fetch("http://localhost:8000/process-audio", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Transcription:", data.transcription);
    console.log("Summary:", data.summary);
    console.log("Translation:", data.translation);
  });
```

---

## Configuration

Edit `config.py` to customize the application:

### Server Settings

```python
SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 8000        # Default port
```

### Summarization Settings

```python
SUMMARY_SENTENCES = 3     # Number of sentences in summary
MIN_SUMMARY_LENGTH = 50   # Minimum chars to summarize
```

### Model Settings

```python
VOSK_MODEL_PATH = "vosk assignment/vosk-model-small-en-us-0.15"
TRANSLATION_MODEL = "thilina/mt5-sinhalese-english"
```

### Upload Settings

```python
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = [".wav", ".mp3", ".m4a", ...]
```

---

## Troubleshooting

### Common Issues

#### 1. "Model not found" Error

**Problem:** Vosk model directory not found

**Solution:**

```bash
# Check if model exists
ls "vosk assignment/vosk-model-small-en-us-0.15"

# If not, download from: https://alphacephei.com/vosk/models
# Extract to: vosk assignment/vosk-model-small-en-us-0.15/
```

#### 2. FFmpeg Not Found

**Problem:** Audio conversion fails

**Solution:**

```bash
# Install FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS

# Verify installation
ffmpeg -version
```

#### 3. Translation Model Download Fails

**Problem:** First time translation fails or is slow

**Solution:**

- Ensure internet connection
- Model downloads automatically on first use (~500MB)
- Subsequent uses will be faster (model cached)

#### 4. Port Already in Use

**Problem:** Port 8000 is occupied

**Solution:**

```python
# Edit config.py or integrated_app.py
SERVER_PORT = 8080  # Use different port
```

#### 5. Out of Memory Error

**Problem:** Translation fails with memory error

**Solution:**

- Process shorter audio files
- Summarize to fewer sentences
- Close other applications
- Consider using CPU instead of GPU

#### 6. Poor Transcription Quality

**Problem:** Transcribed text is inaccurate

**Solutions:**

- Use clearer audio
- Reduce background noise
- Use WAV format (uncompressed)
- Ensure audio is in English
- Try a larger Vosk model

---

## Examples

### Example 1: News Article Audio

**Input Audio:** News broadcast about technology (30 seconds)

**Output:**

- **Transcription:** "Artificial intelligence has revolutionized many industries in recent years. Machine learning algorithms are being used in healthcare, finance, and transportation. Researchers predict that AI will continue to grow and impact society in profound ways. Companies are investing billions in AI development. The technology promises both opportunities and challenges for the future."

- **Summary:** "Artificial intelligence has revolutionized many industries in recent years. Machine learning algorithms are being used in healthcare, finance, and transportation. The technology promises both opportunities and challenges for the future."

- **Translation:** "කෘතිම බුද්ධිය මෑත වසරවලදී බොහෝ කර්මාන්ත විප්ලවීය වෙනසක් කර ඇත. යන්ත්‍ර ඉගෙනුම් ඇල්ගොරිතම සෞඛ්‍ය, මූල්‍ය සහ ප්‍රවාහනයේ භාවිතා වේ. තාක්ෂණය අනාගතය සඳහා අවස්ථා සහ අභියෝග දෙකම පොරොන්දු වේ."

### Example 2: Short Instruction

**Input Audio:** "Please remember to submit your assignment by Friday evening."

**Output:**

- **Transcription:** "please remember to submit your assignment by friday evening"
- **Summary:** "please remember to submit your assignment by friday evening"
- **Translation:** "කරුණාකර සිකුරාදා සන්ධ්‍යාවට පෙර ඔබේ පැවරුම ඉදිරිපත් කිරීමට මතක තබා ගන්න"

### Example 3: Academic Lecture

**Input Audio:** 2-minute lecture excerpt on climate change

**Transcription:** ~200 words
**Summary:** ~50 words (condensed to key points)
**Translation:** Summary in Sinhala

---

## Performance Tips

### For Best Results

1. **Audio Quality:**

   - Use high-quality recordings
   - Minimize background noise
   - Clear speech at moderate pace

2. **File Format:**

   - WAV preferred for quality
   - MP3 acceptable for size

3. **Processing Speed:**

   - First run is slower (model loading)
   - Subsequent runs are faster (cached models)
   - Translation takes the most time

4. **Summary Quality:**
   - Works best with 5+ sentences
   - Clear topic sentences improve results
   - Technical content may need more context

---

## Advanced Usage

### Running on Different Port

```bash
# Method 1: Edit config.py
SERVER_PORT = 8080

# Method 2: Direct in code
python -c "from integrated_app import *; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8080)"
```

### Using with Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "integrated_app.py"]
```

Build and run:

```bash
docker build -t nlp-pipeline .
docker run -p 8000:8000 nlp-pipeline
```

---

## Support

For issues or questions:

1. Check [README.md](README.md) for detailed documentation
2. Run `python test_modules.py` to diagnose issues
3. Check the troubleshooting section above
4. Contact your course instructor

---

**Happy Processing! 🎙️➡️📝➡️🌐**
