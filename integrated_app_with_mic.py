from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from pathlib import Path
import tempfile
import base64

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
    """Serve the main HTML page with microphone support"""
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
            
            .input-section {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
            }
            
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
            }
            
            .tab-button {
                flex: 1;
                padding: 15px;
                border: none;
                background: #f0f0f0;
                cursor: pointer;
                border-radius: 10px;
                font-size: 1.1em;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .tab-button:hover {
                background: #e0e0e0;
            }
            
            .tab-button.active {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                transform: scale(1.05);
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
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
            
            .mic-container {
                text-align: center;
            }
            
            .mic-button {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                border: none;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-size: 4em;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                position: relative;
                margin: 20px auto;
            }
            
            .mic-button:hover {
                transform: scale(1.1);
            }
            
            .mic-button.recording {
                background: #ff4444;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                    box-shadow: 0 10px 30px rgba(255, 68, 68, 0.5);
                }
                50% {
                    transform: scale(1.1);
                    box-shadow: 0 10px 50px rgba(255, 68, 68, 0.8);
                }
            }
            
            .recording-info {
                display: none;
                margin-top: 20px;
                padding: 15px;
                background: #ffe8e8;
                border-radius: 10px;
                color: #cc0000;
            }
            
            .recording-info.active {
                display: block;
            }
            
            .recording-timer {
                font-size: 2em;
                font-weight: bold;
                margin: 10px 0;
            }
            
            .audio-preview {
                display: none;
                margin-top: 20px;
                padding: 20px;
                background: #e8f4fd;
                border-radius: 10px;
            }
            
            .audio-preview.active {
                display: block;
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
            
            .btn-secondary {
                background: #6c757d;
                margin-left: 10px;
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
            
            .mic-instruction {
                color: #666;
                margin-top: 15px;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎙️ NLP Pipeline Application</h1>
                <p>Speech-to-Text → Summarization → Sinhala Translation</p>
            </div>
            
            <div class="input-section">
                <div class="tabs">
                    <button class="tab-button active" onclick="switchTab('upload')">
                        📁 Upload Audio File
                    </button>
                    <button class="tab-button" onclick="switchTab('record')">
                        🎤 Record from Microphone
                    </button>
                </div>
                
                <!-- Upload Tab -->
                <div id="uploadTab" class="tab-content active">
                    <div class="upload-box" id="uploadBox">
                        <div class="upload-icon">🎵</div>
                        <h3>Drop your audio file here or click to browse</h3>
                        <p>Supported formats: WAV, MP3, M4A, OGG, FLAC, etc.</p>
                        <input type="file" id="fileInput" accept="audio/*">
                    </div>
                    <div class="file-info" id="fileInfo"></div>
                    <button class="btn" id="processUploadBtn" disabled>Process Audio</button>
                </div>
                
                <!-- Record Tab -->
                <div id="recordTab" class="tab-content">
                    <div class="mic-container">
                        <h3>Click the microphone to start recording</h3>
                        <button class="mic-button" id="micButton">🎤</button>
                        <div class="recording-info" id="recordingInfo">
                            <div>🔴 Recording in progress...</div>
                            <div class="recording-timer" id="recordingTimer">00:00</div>
                            <div>Click the microphone again to stop</div>
                        </div>
                        <div class="audio-preview" id="audioPreview">
                            <h4>Recording Preview:</h4>
                            <audio controls id="audioPlayer" style="width: 100%; margin-top: 10px;"></audio>
                        </div>
                        <p class="mic-instruction">
                            💡 Speak clearly into your microphone. Click to start/stop recording.
                        </p>
                    </div>
                    <button class="btn" id="processRecordBtn" disabled>Process Recording</button>
                    <button class="btn btn-secondary" id="resetRecordBtn" style="display: none;">Record Again</button>
                </div>
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
            // Check browser compatibility on page load
            window.addEventListener('DOMContentLoaded', () => {
                checkBrowserCompatibility();
            });
            
            function checkBrowserCompatibility() {
                const micContainer = document.querySelector('.mic-container');
                
                // Check if MediaDevices API is available
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    // Show warning in mic tab (but keep tab clickable)
                    if (micContainer) {
                        const warning = document.createElement('div');
                        warning.id = 'browserWarning';
                        warning.style.cssText = `
                            background: #fff3cd;
                            color: #856404;
                            border: 2px solid #ffc107;
                            padding: 20px;
                            border-radius: 10px;
                            margin: 20px 0;
                            text-align: center;
                        `;
                        warning.innerHTML = `
                            <h3>⚠️ Microphone May Not Be Supported</h3>
                            <p><strong>Your browser may not support microphone recording.</strong></p>
                            <p>For best results, use:</p>
                            <ul style="list-style: none; padding: 0;">
                                <li>✅ Chrome (version 47+)</li>
                                <li>✅ Firefox (version 25+)</li>
                                <li>✅ Edge (version 79+)</li>
                            </ul>
                            <p><strong>Current protocol:</strong> ${window.location.protocol}</p>
                            <p style="margin-top: 10px; font-size: 0.9em;">
                                💡 <strong>Tip:</strong> You can still try clicking the microphone button below,
                                or use the "Upload Audio File" tab instead!
                            </p>
                        `;
                        micContainer.insertBefore(warning, micContainer.firstChild);
                    }
                    
                    console.warn('MediaDevices API not available:', {
                        protocol: window.location.protocol,
                        mediaDevices: !!navigator.mediaDevices,
                        getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
                        userAgent: navigator.userAgent
                    });
                } else {
                    console.log('✅ Microphone recording is supported!');
                    console.log('👍 You can use the "Record from Microphone" tab');
                    console.log('📍 Protocol:', window.location.protocol);
                    console.log('🌐 Host:', window.location.host);
                }
            }
            
            // Tab Management
            function switchTab(tab) {
                const tabs = document.querySelectorAll('.tab-button');
                const contents = document.querySelectorAll('.tab-content');
                
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                if (tab === 'upload') {
                    tabs[0].classList.add('active');
                    document.getElementById('uploadTab').classList.add('active');
                } else {
                    tabs[1].classList.add('active');
                    document.getElementById('recordTab').classList.add('active');
                }
                
                // Reset results
                resetUI();
            }
            
            // Upload Tab Logic
            const uploadBox = document.getElementById('uploadBox');
            const fileInput = document.getElementById('fileInput');
            const processUploadBtn = document.getElementById('processUploadBtn');
            const fileInfo = document.getElementById('fileInfo');
            
            let selectedFile = null;
            
            uploadBox.addEventListener('click', () => fileInput.click());
            
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
                processUploadBtn.disabled = false;
                fileInfo.style.display = 'block';
                fileInfo.innerHTML = `
                    <strong>Selected File:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB<br>
                    <strong>Type:</strong> ${file.type}
                `;
            }
            
            processUploadBtn.addEventListener('click', () => {
                if (selectedFile) {
                    processAudio(selectedFile);
                }
            });
            
            // Microphone Recording Logic
            const micButton = document.getElementById('micButton');
            const recordingInfo = document.getElementById('recordingInfo');
            const recordingTimer = document.getElementById('recordingTimer');
            const audioPreview = document.getElementById('audioPreview');
            const audioPlayer = document.getElementById('audioPlayer');
            const processRecordBtn = document.getElementById('processRecordBtn');
            const resetRecordBtn = document.getElementById('resetRecordBtn');
            
            let mediaRecorder = null;
            let audioChunks = [];
            let recordingInterval = null;
            let recordingSeconds = 0;
            let recordedBlob = null;
            
            micButton.addEventListener('click', async () => {
                if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                    await startRecording();
                } else {
                    stopRecording();
                }
            });
            
            async function startRecording() {
                try {
                    // Check if browser supports the MediaDevices API
                    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                        throw new Error(
                            'Your browser does not support microphone recording. ' +
                            'Please use Chrome, Firefox, Edge, or Safari (latest versions). ' +
                            'Also ensure you are accessing via HTTPS or localhost.'
                        );
                    }
                    
                    // Request microphone access
                    const stream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        } 
                    });
                    
                    // Check if MediaRecorder is supported
                    if (!window.MediaRecorder) {
                        throw new Error('MediaRecorder is not supported in your browser.');
                    }
                    
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    recordingSeconds = 0;
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        // Use the actual MIME type from the MediaRecorder
                        recordedBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
                        const audioUrl = URL.createObjectURL(recordedBlob);
                        audioPlayer.src = audioUrl;
                        audioPreview.classList.add('active');
                        processRecordBtn.disabled = false;
                        resetRecordBtn.style.display = 'inline-block';
                    };
                    
                    mediaRecorder.start();
                    micButton.classList.add('recording');
                    recordingInfo.classList.add('active');
                    
                    // Update timer
                    recordingInterval = setInterval(() => {
                        recordingSeconds++;
                        const minutes = Math.floor(recordingSeconds / 60);
                        const seconds = recordingSeconds % 60;
                        recordingTimer.textContent = 
                            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    }, 1000);
                    
                } catch (error) {
                    let errorMessage = 'Error accessing microphone: ';
                    
                    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                        errorMessage += 'Microphone access was denied. Please allow microphone access in your browser settings.';
                    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                        errorMessage += 'No microphone found. Please connect a microphone and try again.';
                    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                        errorMessage += 'Microphone is already in use by another application.';
                    } else if (error.name === 'OverconstrainedError' || error.name === 'ConstraintNotSatisfiedError') {
                        errorMessage += 'Microphone does not meet the required constraints.';
                    } else if (error.name === 'NotSupportedError') {
                        errorMessage += 'HTTPS is required for microphone access (except on localhost).';
                    } else {
                        errorMessage += error.message;
                    }
                    
                    alert(errorMessage);
                    console.error('Microphone error:', error);
                    console.error('Error details:', {
                        name: error.name,
                        message: error.message,
                        navigator: {
                            mediaDevices: !!navigator.mediaDevices,
                            getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
                            protocol: window.location.protocol
                        }
                    });
                }
            }
            
            function stopRecording() {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    micButton.classList.remove('recording');
                    recordingInfo.classList.remove('active');
                    clearInterval(recordingInterval);
                }
            }
            
            resetRecordBtn.addEventListener('click', () => {
                audioPreview.classList.remove('active');
                processRecordBtn.disabled = true;
                resetRecordBtn.style.display = 'none';
                recordedBlob = null;
                recordingTimer.textContent = '00:00';
            });
            
            processRecordBtn.addEventListener('click', () => {
                if (recordedBlob) {
                    // Convert blob to file with appropriate extension
                    // Use .webm extension so server knows to convert it
                    const file = new File([recordedBlob], 'recording.webm', { type: recordedBlob.type });
                    processAudio(file);
                }
            });
            
            // Shared Processing Logic
            const loader = document.getElementById('loader');
            const status = document.getElementById('status');
            const resultsSection = document.getElementById('resultsSection');
            const stepIndicator = document.getElementById('stepIndicator');
            
            async function processAudio(audioFile) {
                // Reset UI
                resetUI();
                resultsSection.style.display = 'none';
                loader.style.display = 'block';
                processUploadBtn.disabled = true;
                processRecordBtn.disabled = true;
                stepIndicator.style.display = 'flex';
                status.style.display = 'block';
                status.className = 'status';
                
                const formData = new FormData();
                formData.append('file', audioFile);
                
                try {
                    // Step 1: Transcription
                    document.getElementById('step1').classList.add('active');
                    status.textContent = 'Step 1: Converting speech to text...';
                    
                    const response = await fetch('/process-audio', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Processing failed');
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
                    processUploadBtn.disabled = false;
                    processRecordBtn.disabled = false;
                    
                } catch (error) {
                    loader.style.display = 'none';
                    status.className = 'status error';
                    status.textContent = '❌ Error: ' + error.message;
                    processUploadBtn.disabled = false;
                    processRecordBtn.disabled = false;
                    console.error('Error:', error);
                }
            }
            
            function resetUI() {
                document.querySelectorAll('.step').forEach(step => {
                    step.classList.remove('active', 'completed');
                });
                status.style.display = 'none';
                stepIndicator.style.display = 'none';
            }
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
    file_path = None
    converted_path = None

    try:
        # Save uploaded file
        file_path = UPLOAD_DIR_PATH / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert audio to WAV format if needed (for Vosk compatibility)
        from pydub import AudioSegment
        import os

        # Check if file is already WAV
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext != ".wav":
            print(f"Converting {file_ext} to WAV format...")
            try:
                # Load audio file (supports mp3, webm, ogg, etc.)
                audio = AudioSegment.from_file(str(file_path))

                # Convert to WAV with proper settings for Vosk
                converted_path = (
                    UPLOAD_DIR_PATH
                    / f"converted_{os.path.splitext(file.filename)[0]}.wav"
                )
                audio.export(
                    str(converted_path),
                    format="wav",
                    parameters=["-ar", "16000", "-ac", "1"],  # 16kHz, mono
                )
                print(f"Converted to WAV: {converted_path}")

                # Use converted file for transcription
                transcription_file = converted_path
            except Exception as conv_error:
                print(
                    f"Warning: Conversion failed ({conv_error}), trying original file..."
                )
                transcription_file = file_path
        else:
            transcription_file = file_path

        # Step 1: Speech to Text
        transcription = transcribe_audio(
            str(transcription_file), model_path=VOSK_MODEL_PATH
        )
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

        # Clean up uploaded file and converted file (if different)
        os.remove(file_path)
        if transcription_file != file_path and os.path.exists(transcription_file):
            os.remove(transcription_file)

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
    print(f"🎤 Microphone Recording: Enabled")
    print("\n💡 Press Ctrl+C to stop the server\n")

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
