import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score, 
    confusion_matrix, classification_report
)

def train_m1():
    print("Loading synthetic transaction data...")
    data_path = 'ml_training/data/transactions_labelled.csv'
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run data generation script first.")
        return

    df = pd.read_csv(data_path)
    
    # Separate features and label
    X = df.drop('is_fraud', axis=1)
    y = df['is_fraud']
    
    print(f"Dataset shape: {df.shape}")
    print(f"Class distribution:\n{y.value_counts()}")
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # Handle class imbalance with SMOTE on training data
    print("Applying SMOTE to balance classes...")
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    print(f"Balanced training distribution:\n{y_train_res.value_counts()}")
    
    # Define models
    print("Defining models for ensemble...")
    xgb = XGBClassifier(
        n_estimators=300, 
        max_depth=6, 
        learning_rate=0.05, 
        use_label_encoder=False, 
        eval_metric='logloss', 
        random_state=42
    )
    
    rf = RandomForestClassifier(
        n_estimators=200, 
        max_depth=10, 
        random_state=42
    )
    
    # Soft Voting Ensemble
    print("Creating VotingClassifier ensemble...")
    ensemble = VotingClassifier(
        estimators=[('xgb', xgb), ('rf', rf)],
        voting='soft',
        weights=[0.6, 0.4]
    )
    
    # Fit models
    print("Training M1 Ensemble (this may take 5-10 minutes)...")
    ensemble.fit(X_train_res, y_train_res)
    
    # Fit individual RF for feature importance later
    rf.fit(X_train_res, y_train_res)
    
    # Evaluate
    print("Evaluating on test set...")
    y_pred = ensemble.predict(X_test)
    y_prob = ensemble.predict_proba(X_test)[:, 1]
    
    auc = roc_auc_score(y_test, y_prob)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    print("-" * 30)
    print(f"AUC-ROC:   {auc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")
    print("-" * 30)
    print("Confusion Matrix:")
    print(cm)
    print("-" * 30)
    
    # Ensure models directory exists
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)
    
    # Save artifacts
    print(f"Saving artifacts to {models_dir}...")
    joblib.dump(ensemble, os.path.join(models_dir, 'm1_scorer.pkl'))
    
    # Feature importance from RF
    feat_importances = dict(zip(X.columns, rf.feature_importances_.astype(float)))
    with open(os.path.join(models_dir, 'm1_feature_importance.json'), 'w') as f:
        json.dump(feat_importances, f, indent=4)
        
    # Metrics
    metrics = {
        'auc_roc': float(auc),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'confusion_matrix': cm.tolist(),
        'timestamp': datetime.now().isoformat()
    }
    with open(os.path.join(models_dir, 'm1_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print("Training complete.")
    if auc > 0.92:
        print("Success: AUC Target Met (>0.92)")
    else:
        print("Warning: AUC Target not reached.")

if __name__ == "__main__":
    from datetime import datetime
    train_m1()
