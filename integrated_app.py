from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from pathlib import Path
import tempfile

# Import custom modules
from vosk_module import transcribe_audio
from summarizer_module import summarize_text
from translator_module import translate_to_sinhala

# Import configuration
try:
    from config import *
except ImportError:
    # Default configuration if config.py not found
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000
    VOSK_MODEL_PATH = "vosk assignment/vosk-model-small-en-us-0.15"
    SUMMARY_SENTENCES = 3
    UPLOAD_DIR = "uploads"
    APP_TITLE = "NLP Pipeline: Speech-to-Text-to-Summary-to-Translation"

app = FastAPI(title=APP_TITLE)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads
UPLOAD_DIR_PATH = Path(UPLOAD_DIR)
UPLOAD_DIR_PATH.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NLP Pipeline - Speech to Sinhala Translation</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .upload-section {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
            }
            
            .upload-box {
                border: 3px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                background: #f8f9ff;
            }
            
            .upload-box:hover {
                background: #e8e9ff;
                border-color: #764ba2;
            }
            
            .upload-box.dragover {
                background: #d8d9ff;
                border-color: #764ba2;
            }
            
            .upload-icon {
                font-size: 3em;
                margin-bottom: 10px;
            }
            
            input[type="file"] {
                display: none;
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 1.1em;
                border-radius: 25px;
                cursor: pointer;
                transition: transform 0.2s;
                margin-top: 20px;
            }
            
            .btn:hover {
                transform: scale(1.05);
            }
            
            .btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .results-section {
                display: none;
            }
            
            .result-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .result-card h2 {
                color: #667eea;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .result-card .content {
                background: #f8f9ff;
                padding: 20px;
                border-radius: 10px;
                line-height: 1.8;
                color: #333;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            
            .loader {
                border: 5px solid #f3f3f3;
                border-top: 5px solid #667eea;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
                display: none;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .status {
                text-align: center;
                padding: 15px;
                background: #e8f4fd;
                border-radius: 10px;
                margin: 20px 0;
                display: none;
                color: #0066cc;
            }
            
            .error {
                background: #ffe8e8;
                color: #cc0000;
            }
            
            .file-info {
                background: #e8f4fd;
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
                display: none;
            }
            
            .step-indicator {
                display: flex;
                justify-content: space-between;
                margin: 30px 0;
                display: none;
            }
            
            .step {
                flex: 1;
                text-align: center;
                padding: 10px;
                background: white;
                margin: 0 5px;
                border-radius: 10px;
                opacity: 0.5;
                transition: all 0.3s;
            }
            
            .step.active {
                opacity: 1;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                transform: scale(1.05);
            }
            
            .step.completed {
                opacity: 1;
                background: #4CAF50;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎙️ NLP Pipeline Application</h1>
                <p>Speech-to-Text → Summarization → Sinhala Translation</p>
            </div>
            
            <div class="upload-section">
                <div class="upload-box" id="uploadBox">
                    <div class="upload-icon">🎵</div>
                    <h3>Drop your audio file here or click to browse</h3>
                    <p>Supported formats: WAV, MP3, M4A, OGG, etc.</p>
                    <input type="file" id="fileInput" accept="audio/*">
                </div>
                <div class="file-info" id="fileInfo"></div>
                <button class="btn" id="processBtn" disabled>Process Audio</button>
            </div>
            
            <div class="step-indicator" id="stepIndicator">
                <div class="step" id="step1">
                    <strong>Step 1</strong><br>Speech to Text
                </div>
                <div class="step" id="step2">
                    <strong>Step 2</strong><br>Summarization
                </div>
                <div class="step" id="step3">
                    <strong>Step 3</strong><br>Translation
                </div>
            </div>
            
            <div class="loader" id="loader"></div>
            <div class="status" id="status"></div>
            
            <div class="results-section" id="resultsSection">
                <div class="result-card">
                    <h2>📝 Transcribed Text (English)</h2>
                    <div class="content" id="transcription"></div>
                </div>
                
                <div class="result-card">
                    <h2>✨ Summary (English)</h2>
                    <div class="content" id="summary"></div>
                </div>
                
                <div class="result-card">
                    <h2>🌐 Translation (Sinhala)</h2>
                    <div class="content" id="translation"></div>
                </div>
            </div>
        </div>
        
        <script>
            const uploadBox = document.getElementById('uploadBox');
            const fileInput = document.getElementById('fileInput');
            const processBtn = document.getElementById('processBtn');
            const loader = document.getElementById('loader');
            const status = document.getElementById('status');
            const resultsSection = document.getElementById('resultsSection');
            const fileInfo = document.getElementById('fileInfo');
            const stepIndicator = document.getElementById('stepIndicator');
            
            let selectedFile = null;
            
            // Click to upload
            uploadBox.addEventListener('click', () => fileInput.click());
            
            // Drag and drop
            uploadBox.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadBox.classList.add('dragover');
            });
            
            uploadBox.addEventListener('dragleave', () => {
                uploadBox.classList.remove('dragover');
            });
            
            uploadBox.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadBox.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFileSelect(files[0]);
                }
            });
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                }
            });
            
            function handleFileSelect(file) {
                selectedFile = file;
                processBtn.disabled = false;
                fileInfo.style.display = 'block';
                fileInfo.innerHTML = `
                    <strong>Selected File:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB<br>
                    <strong>Type:</strong> ${file.type}
                `;
            }
            
            processBtn.addEventListener('click', async () => {
                if (!selectedFile) return;
                
                // Reset UI
                resultsSection.style.display = 'none';
                loader.style.display = 'block';
                processBtn.disabled = true;
                stepIndicator.style.display = 'flex';
                status.style.display = 'block';
                status.className = 'status';
                
                // Reset steps
                document.querySelectorAll('.step').forEach(step => {
                    step.classList.remove('active', 'completed');
                });
                
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                try {
                    // Step 1: Transcription
                    document.getElementById('step1').classList.add('active');
                    status.textContent = 'Step 1: Converting speech to text...';
                    
                    const response = await fetch('/process-audio', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error('Processing failed');
                    }
                    
                    document.getElementById('step1').classList.remove('active');
                    document.getElementById('step1').classList.add('completed');
                    
                    // Step 2: Summarization
                    document.getElementById('step2').classList.add('active');
                    status.textContent = 'Step 2: Generating summary...';
                    
                    const result = await response.json();
                    
                    document.getElementById('step2').classList.remove('active');
                    document.getElementById('step2').classList.add('completed');
                    
                    // Step 3: Translation
                    document.getElementById('step3').classList.add('active');
                    status.textContent = 'Step 3: Translating to Sinhala...';
                    
                    // Small delay to show the step
                    await new Promise(resolve => setTimeout(resolve, 500));
                    
                    document.getElementById('step3').classList.remove('active');
                    document.getElementById('step3').classList.add('completed');
                    
                    // Display results
                    document.getElementById('transcription').textContent = result.transcription;
                    document.getElementById('summary').textContent = result.summary;
                    document.getElementById('translation').textContent = result.translation;
                    
                    loader.style.display = 'none';
                    status.textContent = '✅ Processing completed successfully!';
                    resultsSection.style.display = 'block';
                    processBtn.disabled = false;
                    
                } catch (error) {
                    loader.style.display = 'none';
                    status.className = 'status error';
                    status.textContent = '❌ Error: ' + error.message;
                    processBtn.disabled = false;
                    console.error('Error:', error);
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    """
    Process uploaded audio file through the complete NLP pipeline:
    1. Speech-to-Text (Vosk)
    2. Text Summarization (TF-IDF)
    3. English-to-Sinhala Translation (MT5)
    """
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR_PATH / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Speech to Text
        transcription = transcribe_audio(str(file_path), model_path=VOSK_MODEL_PATH)
        if not transcription:
            raise HTTPException(status_code=500, detail="Transcription failed")

        # Step 2: Summarize the transcribed text
        summary = summarize_text(transcription, num_sentences=SUMMARY_SENTENCES)
        if not summary:
            raise HTTPException(status_code=500, detail="Summarization failed")

        # Step 3: Translate summary to Sinhala
        translation = translate_to_sinhala(summary)
        if not translation:
            raise HTTPException(status_code=500, detail="Translation failed")

        # Clean up uploaded file
        os.remove(file_path)

        return JSONResponse(
            {
                "transcription": transcription,
                "summary": summary,
                "translation": translation,
                "status": "success",
            }
        )

    except Exception as e:
        # Clean up on error
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "NLP Pipeline API is running"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print(f"🚀 Starting {APP_TITLE}")
    print("=" * 60)
    print(f"\n📍 Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"📁 Upload Directory: {UPLOAD_DIR}")
    print(f"🎙️  Vosk Model: {VOSK_MODEL_PATH}")
    print(f"✨ Summary Sentences: {SUMMARY_SENTENCES}")
    print("\n💡 Press Ctrl+C to stop the server\n")

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
