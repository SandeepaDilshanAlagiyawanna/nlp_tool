
"""
Text Summarization Module
Summarizes English text using TF-IDF algorithm
"""

import nltk
import re
import heapq
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import math


# Download NLTK resources if not already downloaded
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


def summarize_text(text, num_sentences=3):
    """
    Summarize text using TF-IDF algorithm

    Args:
        text: Input text to summarize
        num_sentences: Number of sentences in summary (default: 3)

    Returns:
        str: Summarized text or original if too short
    """
    try:
        if not text or len(text.strip()) == 0:
            return ""

        # Clean the text for word tokenization and frequency calculation
        # Remove extra whitespace, numbers in brackets, and non-alphabetic characters
        clean_text_for_words = re.sub(r"\s+", " ", text)
        clean_text_for_words = re.sub(r"\[[0-9]*\]", " ", clean_text_for_words)
        clean_text_for_words = re.sub(r"[^a-zA-Z]", " ", clean_text_for_words)

        # Tokenize sentences (keep original text with punctuation for sentence tokenization)
        sentences = sent_tokenize(text)

        # If text is too short, return as is
        if len(sentences) <= num_sentences:
            return text

        # Tokenize words from cleaned text and convert to lowercase
        words = word_tokenize(clean_text_for_words.lower())

        # Remove stopwords
        stop_words = set(stopwords.words("english"))
        words = [word for word in words if word not in stop_words]

        if len(words) == 0:
            return text

        # Calculate Term Frequency (TF)
        # Count the occurrences of each word
        word_frequencies = {}
        for word in words:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

        # Calculate Inverse Document Frequency (IDF)
        # Determine how common or rare a word is across all sentences
        idf = {}
        num_sentences_count = len(sentences)

        for sentence in sentences:
            # Get unique words in each sentence
            unique_words = set(nltk.word_tokenize(sentence.lower()))
            for word in unique_words:
                # Only consider words that were kept after stopword removal and cleaning
                if word in word_frequencies:
                    if word not in idf:
                        idf[word] = 1
                    else:
                        idf[word] += 1

        # Calculate the IDF score for each word using the logarithmic formula
        for word, count in idf.items():
            idf[word] = math.log(num_sentences_count / (count + 1))

        # Calculate TF-IDF
        # Multiply TF and IDF to get a score for each word that reflects its importance in the document
        tf_idf_scores = {}
        for word, tf in word_frequencies.items():
            if word in idf:
                tf_idf_scores[word] = tf * idf[word]
            else:
                # This case should theoretically not be reached if word_frequencies is based on cleaned words
                tf_idf_scores[word] = 0

        # Score sentences using TF-IDF
        # Sum the TF-IDF scores of the words in each sentence to get a sentence score
        sentence_scores = {}
        for sent in sentences:
            current_sentence_score = 0
            for word in nltk.word_tokenize(sent.lower()):
                if word in tf_idf_scores:
                    current_sentence_score += tf_idf_scores[word]
            sentence_scores[sent] = current_sentence_score

        # Generate Summary (Select top N sentences)
        n = num_sentences  # You can adjust N here to change the number of sentences in the summary
        # Handle case where there are fewer sentences than the desired number of sentences in the summary
        if len(sentences) < n:
            n = len(sentences)

        # Select the top N sentences with the highest TF-IDF scores
        summary_sentences = heapq.nlargest(n, sentence_scores, key=sentence_scores.get)
        # Join the selected sentences to form the summary
        summary = " ".join(summary_sentences)

        print(f"Summarization completed: {len(sentences)} sentences -> {n} sentences")
        return summary

    except Exception as e:
        print(f"Error during summarization: {e}")
        return text  # Return original text if summarization fails


if __name__ == "__main__":
    # Test the module
    test_text = """
    Natural language processing is a subfield of linguistics, computer science, and artificial intelligence 
    concerned with the interactions between computers and human language. In particular, it focuses on how to 
    program computers to process and analyze large amounts of natural language data. The goal is a computer 
    capable of understanding the contents of documents, including the contextual nuances of the language within them. 
    The technology can then accurately extract information and insights contained in the documents as well as 
    categorize and organize the documents themselves. Challenges in natural language processing frequently involve 
    speech recognition, natural language understanding, and natural language generation.
    """
    result = summarize_text(test_text, num_sentences=2)
    print(f"\nOriginal ({len(test_text)} chars):\n{test_text}")
    print(f"\nSummary ({len(result)} chars):\n{result}")
