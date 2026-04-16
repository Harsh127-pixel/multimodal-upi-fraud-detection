import pandas as pd
import numpy as np
import torch
import os
import json
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer
)
import evaluate

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# 1. Load data
DATA_PATH = "ml_training/data/call_transcripts_labelled.csv"
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Data not found! Run generate_synthetic_data.py --type call_transcripts first.")

df = pd.read_csv(DATA_PATH)
df = df.sample(n=min(200, len(df)), random_state=42)
print(f"Loaded {len(df)} samples (optimized for 15-25 min training).")

# 2. Map fraud_pattern to integers
# urgency=0, impersonation=1, money_request=2, secrecy_demand=3, threat=4
LABEL_MAP = {"urgency": 0, "impersonation": 1, "money_request": 2, "secrecy_demand": 3, "threat": 4}
df['label'] = df['fraud_pattern'].map(LABEL_MAP)

MODEL_DIR = "models/m4_intent_classifier"
os.makedirs(MODEL_DIR, exist_ok=True)
with open(os.path.join(MODEL_DIR, "label_map.json"), "w") as f:
    json.dump({v: k for k, v in LABEL_MAP.items()}, f, indent=4)

# 3. Split data
train_texts, test_texts, train_labels, test_labels = train_test_split(
    df['transcript'].values, 
    df['label'].values, 
    test_size=0.2, 
    stratify=df['label'].values, 
    random_state=42
)

# 4. Tokenizer
MODEL_NAME = "google/muril-base-cased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(texts):
    return tokenizer(
        list(texts), 
        padding="max_length", 
        truncation=True, 
        max_length=128
    )

train_encodings = tokenize_function(train_texts)
test_encodings = tokenize_function(test_texts)

# 5. Dataset class
class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = IntentDataset(train_encodings, train_labels)
test_dataset = IntentDataset(test_encodings, test_labels)

# 6. Fine-tune
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=5)

accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1 = f1_metric.compute(predictions=predictions, references=labels, average="weighted")["f1"]
    return {"accuracy": acc, "f1": f1}

training_args = TrainingArguments(
    output_dir=MODEL_DIR,
    num_train_epochs=4,
    per_device_train_batch_size=8, # Reduced for CPU RAM stability
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    logging_steps=25,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

print("Starting training...")
trainer.train()

# 7. Evaluate
print("Evaluating on test set...")
eval_results = trainer.evaluate()
print(f"Final Results: {eval_results}")

# 8. Save
trainer.save_model(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)

# 9. Metrics
with open("models/m4_metrics.json", "w") as f:
    json.dump(eval_results, f, indent=4)

print(f"Model saved to {MODEL_DIR}")
