"""
Advanced English to Sinhala Translation Module
Supports multiple models and fine-tuning options
"""

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    MarianMTModel,
    MarianTokenizer,
)


class TranslationEngine:
    """Advanced translation engine with multiple model support"""

    AVAILABLE_MODELS = {
        "mt5": "thilina/mt5-sinhalese-english",
        "mbart": "facebook/mbart-large-50-many-to-many-mmt",
        # Add more models as needed
    }

    def __init__(self, model_name="mt5"):
        """
        Initialize translation engine

        Args:
            model_name: Model to use ('mt5' or 'mbart')
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self):
        """Load the specified translation model"""
        if self.model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Model '{self.model_name}' not supported. Available: {list(self.AVAILABLE_MODELS.keys())}"
            )

        model_path = self.AVAILABLE_MODELS[self.model_name]
        print(f"Loading {self.model_name} model from {model_path}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

        print(f"✅ {self.model_name} model loaded successfully!")

    def translate(self, text, **kwargs):
        """
        Translate English text to Sinhala with advanced options

        Args:
            text: English text to translate
            **kwargs: Advanced generation parameters
                - num_beams: Number of beams for beam search (default: 8)
                - temperature: Sampling temperature (default: 0.7)
                - max_length: Maximum output length (default: 512)
                - use_context: Use previous sentences for context (default: True)
                - repetition_penalty: Penalty for repetition (default: 1.2)

        Returns:
            str: Translated Sinhala text
        """
        # Default parameters
        params = {
            "num_beams": kwargs.get("num_beams", 8),
            "temperature": kwargs.get("temperature", 0.7),
            "max_length": kwargs.get("max_length", 512),
            "use_context": kwargs.get("use_context", True),
            "repetition_penalty": kwargs.get("repetition_penalty", 1.2),
            "no_repeat_ngram_size": kwargs.get("no_repeat_ngram_size", 3),
            "length_penalty": kwargs.get("length_penalty", 1.2),
            "top_k": kwargs.get("top_k", 50),
            "top_p": kwargs.get("top_p", 0.95),
        }

        if not text or len(text.strip()) == 0:
            return ""

        # Sentence tokenization
        from nltk.tokenize import sent_tokenize

        try:
            import nltk

            nltk.data.find("tokenizers/punkt")
        except:
            import nltk

            nltk.download("punkt", quiet=True)

        sentences = sent_tokenize(text)
        print(
            f"\n🔄 Translating {len(sentences)} sentence(s) using {self.model_name}..."
        )

        translated_sentences = []
        context_buffer = []

        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            print(f"  [{i+1}/{len(sentences)}] {sentence[:60]}...")

            try:
                # Contextual input
                if params["use_context"] and context_buffer:
                    input_text = context_buffer[-1] + " " + sentence
                else:
                    input_text = sentence

                # Tokenize
                inputs = self.tokenizer(
                    input_text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=params["max_length"],
                )

                # Generate translation
                outputs = self.model.generate(
                    **inputs,
                    max_length=params["max_length"],
                    num_beams=params["num_beams"],
                    temperature=params["temperature"],
                    repetition_penalty=params["repetition_penalty"],
                    no_repeat_ngram_size=params["no_repeat_ngram_size"],
                    length_penalty=params["length_penalty"],
                    top_k=params["top_k"],
                    top_p=params["top_p"],
                    early_stopping=True,
                )

                # Decode
                decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

                # Extract new sentence if using context
                if params["use_context"] and context_buffer:
                    parts = decoded.split(". ")
                    translated_sentence = parts[-1] if len(parts) > 1 else decoded
                else:
                    translated_sentence = decoded

                translated_sentences.append(translated_sentence)
                context_buffer.append(sentence)

                # Maintain context window
                if len(context_buffer) > 2:
                    context_buffer.pop(0)

                print(f"    ✓ {translated_sentence[:70]}...")

            except Exception as e:
                print(f"    ✗ Error: {e}")
                continue

        result = " ".join(translated_sentences)
        print(
            f"\n✅ Translation complete: {len(translated_sentences)} sentences, {len(result)} chars\n"
        )
        return result


def translate_to_sinhala_advanced(text, model="mt5", **kwargs):
    """
    Convenience function for advanced translation

    Args:
        text: English text to translate
        model: Model to use ('mt5' or 'mbart')
        **kwargs: Additional generation parameters

    Returns:
        str: Translated Sinhala text
    """
    engine = TranslationEngine(model_name=model)
    return engine.translate(text, **kwargs)


if __name__ == "__main__":
    # Test with your example
    test_text = """the circled notice is one we're trying to influence popular support for the government, 
    and so now we can look one degrees, two degrees, three degrees away from that node and eliminate 
    like three quarters of the diagram outside, that's fear of influence within that sphere."""

    print("=" * 80)
    print("Testing Advanced Translation")
    print("=" * 80)

    # Test with different parameters
    print("\n1️⃣ Standard Translation (num_beams=8):")
    result1 = translate_to_sinhala_advanced(test_text, num_beams=8)
    print(f"Result: {result1}")

    print("\n2️⃣ High Quality (num_beams=10, repetition_penalty=1.5):")
    result2 = translate_to_sinhala_advanced(
        test_text, num_beams=10, repetition_penalty=1.5, temperature=0.8
    )
    print(f"Result: {result2}")

    print("\n3️⃣ Without Context:")
    result3 = translate_to_sinhala_advanced(test_text, use_context=False, num_beams=8)
    print(f"Result: {result3}")
