"""
English to Sinhala Translation Module
Translates English text to Sinhala using MT5 model
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# Global variables to cache the model and tokenizer
_model = None
_tokenizer = None


def load_model():
    """Load the MT5 translation model and tokenizer (cached)"""
    global _model, _tokenizer

    if _model is None or _tokenizer is None:
        print("Loading MT5 Sinhalese-English model...")
        model_name = "thilina/mt5-sinhalese-english"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print("Model loaded successfully!")

    return _model, _tokenizer


def translate_to_sinhala(text, use_context=True):
    """
    Translate English text to Sinhala

    Args:
        text: English text to translate
        use_context: Whether to use contextual translation (default: True)

    Returns:
        str: Translated Sinhala text or empty string if failed
    """
    try:
        if not text or len(text.strip()) == 0:
            return ""

        # Load model
        model, tokenizer = load_model()

        # For long texts, split into sentences and translate separately
        from nltk.tokenize import sent_tokenize

        # Download punkt if needed
        try:
            import nltk

            nltk.data.find("tokenizers/punkt")
        except:
            import nltk

            nltk.download("punkt")

        # Always split into sentences for better translation quality
        sentences = sent_tokenize(text)

        print(f"Translating {len(sentences)} sentence(s)...")

        # Translate sentence by sentence for better results
        translated_sentences = []
        context_buffer = []  # Store previous sentences for context

        for i, sentence in enumerate(sentences):
            if sentence.strip():  # Skip empty sentences
                print(
                    f"  Translating sentence {i+1}/{len(sentences)}: {sentence[:50]}..."
                )

                try:
                    # Add context from previous sentence for better coherence
                    if use_context and context_buffer:
                        # Combine with previous sentence for context
                        contextual_input = context_buffer[-1] + " " + sentence
                    else:
                        contextual_input = sentence

                    inputs = tokenizer(
                        contextual_input,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512,
                    )
                    outputs = model.generate(
                        **inputs,
                        max_length=512,  # Keep reasonable for each sentence
                        num_beams=8,  # Increased from 5 for better quality
                        early_stopping=True,
                        no_repeat_ngram_size=3,  # Increased to avoid more repetition
                        length_penalty=1.2,  # Slightly favor longer, more complete translations
                        temperature=0.7,  # Add some randomness for more natural output
                        top_k=50,  # Limit vocabulary for more focused translations
                        top_p=0.95,  # Nucleus sampling for better coherence
                    )
                    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

                    # If we used context, extract only the new sentence part
                    if use_context and context_buffer:
                        # Split and take the latter part (new translation)
                        parts = decoded.split(". ")
                        translated_sentence = parts[-1] if len(parts) > 1 else decoded
                    else:
                        translated_sentence = decoded

                    translated_sentences.append(translated_sentence)
                    context_buffer.append(sentence)

                    # Keep only last 2 sentences for context
                    if len(context_buffer) > 2:
                        context_buffer.pop(0)

                    print(f"    ✓ Result: {translated_sentence[:60]}...")

                except Exception as e:
                    print(f"    ✗ Error translating sentence {i+1}: {e}")
                    # Skip problematic sentences but continue
                    continue

        # Join all translated sentences
        translated = " ".join(translated_sentences)
        print(
            f"\n✅ Translation completed: {len(translated_sentences)} sentences translated"
        )
        print(f"   Total output length: {len(translated)} characters")
        return translated

    except Exception as e:
        print(f"Error during translation: {e}")
        import traceback

        traceback.print_exc()
        return ""


if __name__ == "__main__":
    # Test the module
    test_text = "Hello, how are you? This is a test of the translation system."
    result = translate_to_sinhala(test_text)
    print(f"\nEnglish: {test_text}")
    print(f"Sinhala: {result}")
