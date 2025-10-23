"""
Text Summarization Module
Summarizes English text using transformer-based model (BART)
"""

# We use Hugging Face's 'transformers' library for the summarization model.
# 'sentencepiece' is required for tokenization in certain models.
try:
    from transformers import pipeline
except ImportError:
    import sys
    import subprocess

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "transformers==4.44.2",
            "sentencepiece",
        ]
    )
    from transformers import pipeline

# The pipeline function simplifies using pre-trained models.
# We use the 'summarization' pipeline with Facebook's BART model.
# Initialize the model once when the module is imported
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_text(text, num_sentences=3):
    """
    Summarize text using transformer-based model (BART)

    Args:
        text: Input text to summarize
        num_sentences: Number of sentences in summary (default: 3)
                      Note: This is used to estimate max_length for the model

    Returns:
        str: Summarized text or original if too short
    """
    try:
        if not text or len(text.strip()) == 0:
            return ""

        # Estimate max_length based on desired number of sentences
        # Approximate: ~25-30 words per sentence = ~30-35 tokens per sentence
        # For 100 words (4 sentences), we need ~120-140 tokens
        # Increased both max and min to ensure longer, more detailed summaries
        max_length = min(
            num_sentences * 35, 500
        )  # Increased cap to 500 tokens for much longer summaries
        min_length = max(80, num_sentences * 20)  # Minimum 80 tokens (~60-70 words)

        # Use the summarization model
        result = summarizer(
            text, max_length=max_length, min_length=min_length, do_sample=False
        )
        summary = result[0]["summary_text"]

        print(
            f"Summarization completed: Generated summary with ~{len(summary.split())} words"
        )
        return summary

    except Exception as e:
        print(f"Error during summarization: {e}")
        return text  # Return original text if summarization fails


if __name__ == "__main__":
    # Test the module with interactive input
    try:
        from rouge_score import rouge_scorer
    except ImportError:
        import sys
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "rouge-score"])
        from rouge_score import rouge_scorer

    # Enter custom text to test summarization.
    user_text = input("\nEnter your own paragraph for summarization:\n\n")

    if len(user_text.strip()) > 0:
        result = summarize_text(user_text, num_sentences=3)
        print("\n Summary:\n")
        print(result)

        # Evaluate Summary Quality using ROUGE
        scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
        scores = scorer.score(user_text, result)
        print("\n📊 ROUGE Evaluation Metrics:\n", scores)
    else:
        print("⚠️ No input text provided.")
