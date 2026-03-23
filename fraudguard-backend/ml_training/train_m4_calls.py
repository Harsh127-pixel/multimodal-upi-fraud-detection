import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import os
import json
import evaluate

# 1. Setup
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# 2. Load Data
DATA_PATH = "ml_training/data/call_transcripts_labelled.csv"
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Data not found! Run generate_synthetic_data.py --type call_transcripts first.")

df = pd.read_csv(DATA_PATH)
df = df.sample(n=min(2000, len(df)), random_state=42)
print(f"Loaded {len(df)} voice transcripts (subsampled for speed).")

# Label mapping
LABELS = ["urgency", "impersonation", "money_request", "secrecy_demand", "threat"]
label2id = {label: i for i, label in enumerate(LABELS)}
id2label = {i: label for i, label in enumerate(LABELS)}

df['label'] = df['fraud_pattern'].map(label2id)

# 3. Tokenizer
MODEL_NAME = "google/muril-base-cased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(texts):
    return tokenizer(texts, padding="max_length", truncation=True, max_length=128)

# 4. Dataset Class
class CallDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# 5. Prepare Data
train_texts, test_texts, train_labels, test_labels = train_test_split(
    df['transcript'].tolist(), df['label'].tolist(), test_size=0.2, random_state=42, stratify=df['label']
)

train_encodings = tokenize_function(train_texts)
test_encodings = tokenize_function(test_texts)

train_dataset = CallDataset(train_encodings, train_labels)
test_dataset = CallDataset(test_encodings, test_labels)

# 6. Model
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=len(LABELS),
    id2label=id2label,
    label2id=label2id
)

# 7. Metrics
metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# 8. Training
OUTPUT_DIR = "models/m4_call_analyzer"
training_args = TrainingArguments(
    output_dir="./tmp/m4_results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir="./tmp/m4_logs",
    logging_steps=50,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    push_to_hub=False
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics
)

print("Starting M4 training...")
trainer.train()

# 9. Save
print(f"Saving M4 model to {OUTPUT_DIR}...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# 10. Final Metrics
eval_results = trainer.evaluate()
print(f"M4 Final Evaluation: {eval_results}")

with open("models/m4_metrics.json", "w") as f:
    json.dump(eval_results, f, indent=2)

print("M4 Training Complete.")
