# Configuration file for NLP Pipeline Application

# Server Configuration
SERVER_HOST = "0.0.0.0"  # Use "127.0.0.1" for localhost only
SERVER_PORT = 8000

# Vosk Speech-to-Text Configuration
VOSK_MODEL_PATH = "vosk assignment/vosk-model-small-en-us-0.15"
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_SAMPLE_WIDTH = 2

# Summarization Configuration
SUMMARY_SENTENCES = 3  # Number of sentences in summary
MIN_SUMMARY_LENGTH = 50  # Minimum characters for summarization

# Translation Configuration
TRANSLATION_MODEL = "thilina/mt5-sinhalese-english"
MAX_TRANSLATION_LENGTH = 512  # Per sentence output length
TRANSLATION_NUM_BEAMS = 5  # Higher = better quality but slower (1-10)

# Upload Configuration
UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB in bytes
ALLOWED_EXTENSIONS = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4", ".avi"]

# Processing Configuration
CLEANUP_TEMP_FILES = True  # Remove temporary files after processing
SAVE_RESULTS = False  # Save results to disk (optional)
RESULTS_DIR = "results"

# UI Configuration
APP_TITLE = "NLP Pipeline: Speech-to-Text-to-Summary-to-Translation"
APP_DESCRIPTION = "Upload audio → Get transcription, summary, and Sinhala translation"

# Debug Configuration
DEBUG_MODE = False
VERBOSE_LOGGING = True
