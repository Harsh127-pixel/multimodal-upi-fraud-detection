import pandas as pd
import numpy as np
import argparse
import random
import os
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Generate synthetic training data for FraudGuard.")
    parser.add_argument("--type", type=str, required=True, choices=["transactions", "sms_hindi", "call_transcripts"], help="Type of data to generate")
    parser.add_argument("--count", type=int, default=1000, help="Number of rows to generate")
    return parser.parse_args()

def generate_transactions(count):
    # Features from feature_eng.py logic
    TIME_OF_DAY_RISK = {
        0: 0.9, 1: 1.0, 2: 1.0, 3: 1.0, 4: 0.9, 5: 0.7,
        6: 0.4, 7: 0.2, 8: 0.1, 9: 0.1, 10: 0.1, 11: 0.1,
        12: 0.1, 13: 0.1, 14: 0.1, 15: 0.1, 16: 0.1, 17: 0.1,
        18: 0.2, 19: 0.3, 20: 0.4, 21: 0.5, 22: 0.6, 23: 0.8
    }
    
    data = []
    columns = [
        "upi_age_days", "registration_state_risk", "tx_velocity_1hr", "tx_velocity_24hr", "tx_velocity_7d",
        "amount", "amount_deviation", "time_of_day_risk", "is_weekend", "is_post_call",
        "payee_payer_graph_distance", "payer_account_age_days", "device_match", "is_new_payee",
        "payee_blacklist_score", "amount_round_number", "is_high_value", "hour_of_day", "is_fraud"
    ]
    
    for i in range(count):
        if i % 10000 == 0 and i > 0:
            print(f"Progress: {i}/{count} rows generated")
            
        is_fraud = 1 if random.random() < 0.05 else 0
        
        if is_fraud:
            upi_age_days = random.randint(1, 30)
            amount = random.uniform(1000, 50000)
            tx_velocity_1hr = random.randint(3, 15)
            is_post_call = 1 if random.random() < 0.6 else 0
            is_new_payee = 1 if random.random() < 0.8 else 0
            payee_blacklist_score = random.uniform(0.5, 1.0)
            amount_round_number = 1 if random.random() < 0.7 else 0
            device_match = random.randint(0, 1) # Fraud might or might not match
        else:
            upi_age_days = random.randint(30, 3650)
            amount = random.uniform(50, 50000)
            tx_velocity_1hr = random.randint(0, 3)
            is_post_call = 0
            is_new_payee = 0
            payee_blacklist_score = 0.0
            amount_round_number = 1 if amount % 100 == 0 else 0
            device_match = 1
            
        registration_state_risk = random.uniform(0.1, 0.9)
        tx_velocity_24hr = tx_velocity_1hr + random.randint(0, 10)
        tx_velocity_7d = tx_velocity_24hr + random.randint(0, 50)
        amount_deviation = amount * random.uniform(-0.2, 2.0) if is_fraud else amount * random.uniform(-0.1, 0.1)
        hour_of_day = random.randint(0, 23)
        time_of_day_risk = TIME_OF_DAY_RISK[hour_of_day]
        is_weekend = random.randint(0, 1)
        payee_payer_graph_distance = random.randint(1, 10) if not is_fraud else random.randint(5, 20)
        payer_account_age_days = upi_age_days + random.randint(0, 1000)
        is_high_value = 1 if amount > 10000 else 0
        
        # Add noise
        noise_factor = 1.0 + random.uniform(-0.05, 0.05)
        upi_age_days *= noise_factor
        amount *= noise_factor
        amount_deviation *= noise_factor
        registration_state_risk *= noise_factor
        tx_velocity_1hr *= noise_factor
        
        data.append([
            upi_age_days, registration_state_risk, tx_velocity_1hr, tx_velocity_24hr, tx_velocity_7d,
            amount, amount_deviation, time_of_day_risk, is_weekend, is_post_call,
            payee_payer_graph_distance, payer_account_age_days, device_match, is_new_payee,
            payee_blacklist_score, amount_round_number, is_high_value, float(hour_of_day), is_fraud
        ])
        
    df = pd.DataFrame(data, columns=columns)
    return df

def generate_sms(count):
    fraud_templates = [
        "OTP share karein", "account band ho jayega", "prize jeetein hai aap",
        "turant transfer karein", "KYC update karein", "aapka account block ho gaya",
        "Rs {amount} ka reward claim karein", "verify karne ke liye click karein",
        "bank manager bol raha hoon", "ek baar OTP batao bas"
    ]
    legit_templates = [
        "Rs {amount} credited to your account", "Payment of Rs {amount} to {upi} successful",
        "Your UPI transaction of Rs {amount} is complete"
    ]
    
    urgency_words = ["URGENT", "IMMEDIATE", "LAST WARNING", "NOW"]
    upi_ids = ["user1@okaxis", "scam.99@paytm", "bank.support@icici", "customer.care@sbi"]
    
    data = []
    for i in range(count):
        if i % 10000 == 0 and i > 0:
            print(f"Progress: {i}/{count} rows generated")
            
        is_fraud = 1 if i < count // 2 else 0
        amount = random.randint(100, 50000)
        upi = random.choice(upi_ids)
        
        if is_fraud:
            base = random.choice(fraud_templates).format(amount=amount)
            if random.random() < 0.5:
                base = f"{random.choice(urgency_words)}: {base}"
            if random.random() < 0.3:
                base = f"{base}. Click here: http://bit.ly/fake-bank"
            text = base
        else:
            text = random.choice(legit_templates).format(amount=amount, upi=upi)
            
        data.append([text, is_fraud])
        
    df = pd.DataFrame(data, columns=["text", "is_fraud"])
    return df

def generate_calls(count):
    patterns = {
        "urgency": "Aapka account 2 ghante mein band ho jayega. Abhi OTP share karein.",
        "impersonation": "Main aapke bank ka manager bol raha hoon. Aapki KYC incomplete hai.",
        "money_request": "Sir mujhe 5000 rupaye ki zaroorat hai. Please turant transfer karo.",
        "secrecy_demand": "Yeh baat kisi ko mat batana. Sirf hamare beech mein rakho.",
        "threat": "Agar aapne cooperate nahi kiya toh aapka account permanently block ho jayega."
    }
    
    pattern_keys = list(patterns.keys())
    data = []
    for i in range(count):
        pattern_key = pattern_keys[i % 5]
        transcript = patterns[pattern_key]
        # Add some variation
        if i % 2 == 0:
            transcript = f"Hello. {transcript}"
        else:
            transcript = f"{transcript} Do you understand?"
            
        data.append([transcript, pattern_key])
        
    df = pd.DataFrame(data, columns=["transcript", "fraud_pattern"])
    return df

def main():
    args = parse_args()
    
    print(f"Generating {args.count} rows of type {args.type}...")
    
    if args.type == "transactions":
        df = generate_transactions(args.count)
    elif args.type == "sms_hindi":
        df = generate_sms(args.count)
    elif args.type == "call_transcripts":
        df = generate_calls(args.count)
        
    output_dir = "ml_training/data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{args.type}_labelled.csv"
    
    df.to_csv(output_path, index=False)
    
    fraud_count = len(df[df.iloc[:, -1] == 1]) if args.type != "call_transcripts" else len(df)
    legit_count = len(df) - fraud_count if args.type != "call_transcripts" else 0
    
    print("\nGeneration Summary:")
    print(f"File Path: {output_path}")
    print(f"Row Count: {len(df)}")
    if args.type != "call_transcripts":
        print(f"Fraud Count: {fraud_count}")
        print(f"Legitimate Count: {legit_count}")
    else:
        print(f"Patterns: {df['fraud_pattern'].unique().tolist()}")

if __name__ == "__main__":
    main()
