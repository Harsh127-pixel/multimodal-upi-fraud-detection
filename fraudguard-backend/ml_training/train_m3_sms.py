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
DATA_PATH = "ml_training/data/sms_hindi_labelled.csv"
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} samples.")

# 2. Split data
train_texts, test_texts, train_labels, test_labels = train_test_split(
    df['text'].values, 
    df['is_fraud'].values, 
    test_size=0.2, 
    stratify=df['is_fraud'].values, 
    random_state=42
)

# 3. Tokenizer
# Replacing ai4bharat/indic-bert with google/muril-base-cased as indic-bert is currently gated and requires login.
# MURIL is a powerful alternative for Indic languages.
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

# 4. Dataset class
class SMSDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = SMSDataset(train_encodings, train_labels)
test_dataset = SMSDataset(test_encodings, test_labels)

# 5. Model
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

# 6. Metrics
accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1 = f1_metric.compute(predictions=predictions, references=labels)["f1"]
    return {"accuracy": acc, "f1": f1}

# 7. Training Arguments
# If CPU, reduce epochs/batch size for speed? User said 3 epochs and 16/32 batch size.
output_dir = "models/m3_sms_classifier"
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    logging_steps=50,
    weight_decay=0.01,
    learning_rate=2e-5,
    push_to_hub=False,
    report_to="none"
)

# 8. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

# 9. Fine-tune
print("Starting training...")
trainer.train()

# 10. Evaluate and Save
print("Evaluating on test set...")
eval_results = trainer.evaluate()
print(f"Final Results: {eval_results}")

os.makedirs(output_dir, exist_ok=True)
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

# Save metrics to JSON
metrics_path = "models/m3_metrics.json"
with open(metrics_path, "w") as f:
    json.dump(eval_results, f, indent=4)

print(f"Model and metrics saved to {output_dir}")
