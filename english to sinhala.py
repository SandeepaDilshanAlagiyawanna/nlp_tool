from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
from nltk.translate.bleu_score import sentence_bleu

# 1. Load your dataset
df = pd.read_csv("dataset/data.csv")
print("Dataset loaded:")
print(df.head())

# 2. Load the mt5-sinhalese-english model & tokenizer
model_name = "thilina/mt5-sinhalese-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 3. Translation function (English → Sinhala)
def translate_en_to_si_mt5(text):
    # Prefixing or prompt format may help — sometimes models require a task hint
    input_text = text
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(**inputs, max_length=200)
    translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated

# 4. Use your dataset to translate English → Sinhala
df["Predicted_Sinhala"] = df["English"].apply(translate_en_to_si_mt5)

# 5. Evaluate using BLEU
bleu_scores = []
for i in range(len(df)):
    reference = [str(df.loc[i, "Sinhala"]).split()]
    candidate = str(df.loc[i, "Predicted_Sinhala"]).split()
    score = sentence_bleu(reference, candidate)
    bleu_scores.append(score)

df["BLEU"] = bleu_scores

# 6. Save results
df.to_csv("mt5_translated_results.csv", index=False)
print("Translation done. Saved to mt5_translated_results.csv")

# 7. Show samples and average BLEU
print(df.head())
print("Average BLEU:", sum(bleu_scores) / len(bleu_scores))
