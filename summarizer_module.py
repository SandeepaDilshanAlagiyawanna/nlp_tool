# We use Hugging Face's 'transformers' library for the summarization model.
# 'sentencepiece' is required for tokenization in certain models.
# If the required packages are not installed, install them programmatically.
try:
    from transformers import pipeline
except ImportError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers==4.44.2", "sentencepiece"])
    from transformers import pipeline

# The pipeline function simplifies using pre-trained models.
# We use the 'summarization' pipeline with Facebook's BART model.
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Enter custom text to test summarization.
user_text = input("\nEnter your own paragraph for summarization:\n\n")

if len(user_text.strip()) > 0:
    # Use a reasonable max_length for the model (e.g., 512) to avoid tokenization errors.
    result = summarizer(user_text, max_length=512, min_length=20, do_sample=False)
    print("\n Summary:\n")
    print(result[0]['summary_text'])
else:
    print("⚠️ No input text provided.")


# Evaluate Summary Quality
# ROUGE (Recall-Oriented Understudy for Gisting Evaluation) is a common metric for measuring summarization quality.
try:
    from rouge_score import rouge_scorer
except ImportError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rouge-score"])
    from rouge_score import rouge_scorer

# Initialize ROUGE scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)

# Compute scores (use the original input text and the generated summary)
if len(user_text.strip()) > 0:
    scores = scorer.score(user_text, result[0]['summary_text'])
    print("\n📊 ROUGE Evaluation Metrics:\n", scores)