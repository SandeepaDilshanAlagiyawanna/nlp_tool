import nltk
import re
import heapq
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import math

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')

user_text = input("Enter your own paragraph for summarization:\n\n")

if len(user_text.strip()) > 0:
    # Clean the text (keep punctuation for sentence tokenization)
    clean_text_for_words = re.sub(r'\s+', ' ', user_text)
    clean_text_for_words = re.sub(r'\[[0-9]*\]', ' ', clean_text_for_words)
    clean_text_for_words = re.sub(r'[^a-zA-Z]', ' ', clean_text_for_words)

    # Tokenize sentences
    sentences = sent_tokenize(user_text)

    # Tokenize words from cleaned text for frequency calculation
    words = word_tokenize(clean_text_for_words.lower())

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words]

    # Calculate Term Frequency (TF)
    word_frequencies = {}
    for word in words:
        if word not in word_frequencies:
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

    # Calculate Inverse Document Frequency (IDF)
    idf = {}
    num_sentences = len(sentences)

    for sentence in sentences:
        unique_words = set(nltk.word_tokenize(sentence.lower()))
        for word in unique_words:
            if word in word_frequencies: # Only consider words that are not stopwords/punctuation
                if word not in idf:
                    idf[word] = 1
                else:
                    idf[word] += 1

    for word, count in idf.items():
        idf[word] = math.log(num_sentences / (count + 1))

    # Calculate TF-IDF
    tf_idf_scores = {}
    for word, tf in word_frequencies.items():
        if word in idf:
            tf_idf_scores[word] = tf * idf[word]
        else:
            tf_idf_scores[word] = 0 # Should not happen if word_frequencies is based on cleaned words

    # Score sentences using TF-IDF
    sentence_scores = {}
    for sent in sentences:
        current_sentence_score = 0
        for word in nltk.word_tokenize(sent.lower()):
            if word in tf_idf_scores:
                current_sentence_score += tf_idf_scores[word]
        sentence_scores[sent] = current_sentence_score

    # Generate Summary (Select top N sentences)
    n = 3  # You can adjust N here
    # Handle case where there are fewer sentences than n
    if len(sentences) < n:
        n = len(sentences)
    summary_sentences = heapq.nlargest(n, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)

    print("\nSummary:\n")
    print(summary)
else:
    print("No input text provided.")