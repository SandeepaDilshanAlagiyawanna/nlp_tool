# 🏗️ Project Architecture

## Overview

This NLP Pipeline application integrates three distinct NLP tools into a unified web application using FastAPI.

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (User)                       │
│                  http://localhost:8000                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP Request (Audio File)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                           │
│                  (integrated_app.py)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Processes through pipeline
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Module 1   │   │   Module 2   │   │   Module 3   │
│              │   │              │   │              │
│ Speech-to-   │──▶│ Text         │──▶│ English-to-  │
│ Text (Vosk)  │   │ Summarizer   │   │ Sinhala MT5  │
│              │   │ (TF-IDF)     │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
   Audio Input      Text Output       Summary Output

        │                  │                   │
        └──────────────────┴───────────────────┘
                            │
                            ▼
                    JSON Response
        {
          "transcription": "...",
          "summary": "...",
          "translation": "..."
        }
```

## Module Details

### 1. Speech-to-Text Module (`vosk_module.py`)

**Technology:** Vosk (Offline Speech Recognition)

**Input:** Audio file (WAV, MP3, M4A, etc.)

**Process:**

1. Convert audio to WAV format (mono, 16kHz, 16-bit)
2. Load Vosk model
3. Process audio in chunks
4. Recognize speech and convert to text

**Output:** English text transcription

**Dependencies:**

- vosk
- pydub
- wave
- AudioSegment

**Model:** `vosk-model-small-en-us-0.15`

---

### 2. Summarization Module (`summarizer_module.py`)

**Technology:** TF-IDF (Term Frequency-Inverse Document Frequency)

**Input:** English text (from transcription)

**Process:**

1. Tokenize text into sentences and words
2. Remove stopwords
3. Calculate TF (term frequency) for each word
4. Calculate IDF (inverse document frequency)
5. Compute TF-IDF scores
6. Score sentences based on word importance
7. Select top N sentences with highest scores

**Output:** Summarized English text

**Dependencies:**

- nltk
- re
- heapq
- math

**Algorithm:**

```
TF-IDF(word) = TF(word) × IDF(word)

Where:
- TF(word) = frequency of word in document
- IDF(word) = log(total_sentences / sentences_containing_word)

Sentence_Score = Σ TF-IDF(word) for all words in sentence
```

---

### 3. Translation Module (`translator_module.py`)

**Technology:** MT5 (Multilingual T5 Transformer)

**Input:** English summary text

**Process:**

1. Load MT5 model (cached after first load)
2. Tokenize input text
3. Generate translation using transformer model
4. Decode output tokens to Sinhala text

**Output:** Sinhala translation

**Dependencies:**

- transformers
- torch
- sentencepiece

**Model:** `thilina/mt5-sinhalese-english`

---

## File Structure

```
NLP tool Development/
│
├── integrated_app.py          # Main FastAPI application
│   ├── Web UI (HTML/CSS/JS embedded)
│   ├── API endpoints
│   └── Pipeline orchestration
│
├── vosk_module.py             # Speech-to-Text module
├── summarizer_module.py       # Summarization module
├── translator_module.py       # Translation module
├── config.py                  # Configuration settings
│
├── requirements.txt           # Python dependencies
├── start.sh                   # Startup script
├── test_modules.py            # Testing script
│
├── README.md                  # Main documentation
├── QUICKSTART.md              # Quick start guide
├── USER_GUIDE.md              # Detailed user guide
├── ARCHITECTURE.md            # This file
│
├── uploads/                   # Temporary upload directory
│
├── vosk assignment/
│   ├── vosk-model-small-en-us-0.15/  # Vosk model
│   ├── audio_transcriber.py   # Original transcriber
│   ├── main.py                # Original main
│   └── audios/                # Test audio files
│
├── english to sinhala.py      # Original translation script
└── summerize.py               # Original summarization script
```

## Data Flow

### Complete Pipeline Flow

```
1. User uploads audio file
   │
   ├─▶ File saved to uploads/
   │
2. Speech-to-Text Processing
   │
   ├─▶ Audio converted to WAV (if needed)
   ├─▶ Vosk model processes audio
   ├─▶ Returns: "This is the transcribed text..."
   │
3. Text Summarization
   │
   ├─▶ Tokenize into sentences
   ├─▶ Calculate TF-IDF scores
   ├─▶ Select top 3 sentences
   ├─▶ Returns: "This is the summary..."
   │
4. Translation
   │
   ├─▶ Load MT5 model
   ├─▶ Tokenize English text
   ├─▶ Generate Sinhala translation
   ├─▶ Returns: "මෙය සිංහල පරිවර්තනයයි..."
   │
5. Return all results as JSON
   │
   └─▶ Display in web UI
```

## API Architecture

### Endpoints

```
GET /
├─ Returns: HTML web interface
└─ Content: Full single-page application

POST /process-audio
├─ Input: Audio file (multipart/form-data)
├─ Process: Run through 3-module pipeline
└─ Returns: JSON with transcription, summary, translation

GET /health
├─ Returns: Server health status
└─ Content: {"status": "healthy", "message": "..."}
```

### Request/Response Flow

```
Client Request:
POST /process-audio
Content-Type: multipart/form-data
File: audio.wav (10MB)

↓

Server Processing:
1. Save file → uploads/audio.wav
2. vosk_module.transcribe_audio() → "text..."
3. summarizer_module.summarize_text() → "summary..."
4. translator_module.translate_to_sinhala() → "පරිවර්තනය..."
5. Delete uploads/audio.wav

↓

Server Response:
{
  "transcription": "Full English text from audio...",
  "summary": "Condensed summary...",
  "translation": "සිංහල පරිවර්තනය...",
  "status": "success"
}
```

## Technology Stack

### Backend

- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **Language:** Python 3.8+

### NLP Technologies

- **Speech Recognition:** Vosk 0.3.45
- **Text Processing:** NLTK 3.8.1
- **Translation:** Transformers 4.35.2
- **Deep Learning:** PyTorch 2.1.1

### Audio Processing

- **Library:** pydub 0.25.1
- **Converter:** FFmpeg

### Frontend

- **HTML5** - Structure
- **CSS3** - Styling (embedded)
- **JavaScript (Vanilla)** - Interactivity
- **Fetch API** - HTTP requests

## Performance Characteristics

### Processing Time (Approximate)

| Step          | Time       | Notes                         |
| ------------- | ---------- | ----------------------------- |
| Upload        | 1-5s       | Depends on file size          |
| Transcription | 5-15s      | Depends on audio length       |
| Summarization | <1s        | Very fast (TF-IDF)            |
| Translation   | 3-10s      | First run slower (model load) |
| **Total**     | **10-30s** | For 30-60s audio              |

### Resource Usage

| Resource | Usage   | Notes                       |
| -------- | ------- | --------------------------- |
| RAM      | 2-4 GB  | Mainly for MT5 model        |
| CPU      | Medium  | During transcription        |
| Disk     | ~1 GB   | For models                  |
| Network  | ~500 MB | First run (download models) |

## Scalability Considerations

### Current Limitations

- Single request processing (sequential)
- Models loaded in memory (not shared)
- No queue system for concurrent requests

### Potential Improvements

1. **Add request queue** (Celery, RQ)
2. **Implement caching** (Redis)
3. **Use async processing** (already async-capable)
4. **Model optimization** (quantization, ONNX)
5. **Load balancing** (multiple workers)
6. **Database storage** (save results)

## Security Considerations

### Current Implementation

- File size limits (100MB)
- Allowed file extensions validation
- Temporary file cleanup
- CORS enabled (development)

### Production Recommendations

1. Add authentication (JWT, OAuth)
2. Rate limiting (slowapi)
3. Input validation (file type verification)
4. Virus scanning for uploads
5. HTTPS only
6. Restrict CORS origins
7. Add logging and monitoring

## Extension Points

### Easy Customizations

1. **Add more languages:**

   - Include additional MT5 models
   - Add language selection in UI

2. **Improve summarization:**

   - Use extractive models (BERT)
   - Add abstractive summarization

3. **Better speech recognition:**

   - Use larger Vosk models
   - Add language detection
   - Support multiple languages

4. **Save results:**

   - Add database (SQLite, PostgreSQL)
   - Create user accounts
   - History of processed files

5. **Audio enhancements:**
   - Noise reduction pre-processing
   - Speaker diarization
   - Timestamps for transcription

---

## Development Workflow

### Adding a New Module

```python
# 1. Create module file: new_module.py
def process_text(text):
    # Your processing logic
    return processed_text

# 2. Import in integrated_app.py
from new_module import process_text

# 3. Add to pipeline in process_audio()
step4_result = process_text(translation)

# 4. Update response
return JSONResponse({
    "transcription": transcription,
    "summary": summary,
    "translation": translation,
    "new_output": step4_result
})

# 5. Update UI to display new output
```

### Testing Workflow

```bash
# 1. Test individual modules
python vosk_module.py
python summarizer_module.py
python translator_module.py

# 2. Run comprehensive tests
python test_modules.py

# 3. Test API manually
python integrated_app.py
# Then use browser or curl

# 4. Integration testing
# Upload various audio files through UI
```

---

**Architecture Version:** 1.0  
**Last Updated:** October 2025  
**Course:** CM3620 - Natural Language Processing
