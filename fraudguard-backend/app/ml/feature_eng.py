import numpy as np
from datetime import datetime

class FeatureExtractor:
    """
    Feature extractor for UPI fraud detection.
    Extracts 18 key features from a transaction dictionary.
    """
    
    # Pre-calculated risk scores for each hour of the day (0-23)
    # Higher risk during night hours (0-5 AM) and late night (11 PM)
    TIME_OF_DAY_RISK = {
        0: 0.9, 1: 1.0, 2: 1.0, 3: 1.0, 4: 0.9, 5: 0.7,
        6: 0.4, 7: 0.2, 8: 0.1, 9: 0.1, 10: 0.1, 11: 0.1,
        12: 0.1, 13: 0.1, 14: 0.1, 15: 0.1, 16: 0.1, 17: 0.1,
        18: 0.2, 19: 0.3, 20: 0.4, 21: 0.5, 22: 0.6, 23: 0.8
    }

    def __init__(self, redis_client=None):
        self.redis = redis_client

    def extract(self, tx: dict) -> np.ndarray:
        """Alias for extract_features with user-requested name."""
        return self.extract_features(tx)

    def extract_features(self, tx: dict) -> np.ndarray:
        """
        Extracts 18 features from the transaction dictionary.
        Returns: np.ndarray of shape (18,)
        Performance: <5ms per call
        """
        # 1. upi_age_days
        upi_age_days = float(tx.get('upi_age_days', 0))
        
        # 2. registration_state_risk
        registration_state_risk = float(tx.get('registration_state_risk', 0.0))
        
        # 3. tx_velocity_1hr
        # In a real system, these would be fetched from Redis if redis_client is present.
        # For now, we use the values passed in 'tx' or 0.0 as fallback.
        tx_velocity_1hr = float(tx.get('tx_velocity_1hr', 0))
        
        # 4. tx_velocity_24hr
        tx_velocity_24hr = float(tx.get('tx_velocity_24hr', 0))
        
        # 5. tx_velocity_7d
        tx_velocity_7d = float(tx.get('tx_velocity_7d', 0))
        
        # 6. amount
        amount = float(tx.get('amount', 0))
        
        # 7. amount_deviation_from_user_baseline
        # If not provided, calculate assuming 'user_baseline_amount' is present
        amount_deviation = float(tx.get('amount_deviation_from_user_baseline', 
                                     amount - tx.get('user_baseline_amount', amount)))
        
        # Get time-based info
        ts = tx.get('timestamp')
        if not isinstance(ts, datetime):
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except ValueError:
                    ts = datetime.utcnow()
            else:
                # Fallback to current time if missing or wrong type
                ts = datetime.utcnow()
            
        hour = ts.hour
        is_weekend = 1 if ts.weekday() >= 5 else 0
        
        # 8. time_of_day_risk
        time_of_day_risk = self.TIME_OF_DAY_RISK.get(hour, 0.1)
        
        # 9. is_weekend
        # Calculated above
        
        # 10. is_post_call (1 if unknown call in last 5 minutes)
        is_post_call = 1 if tx.get('is_post_call') else 0
        
        # 11. payee_payer_graph_distance
        graph_dist = float(tx.get('payee_payer_graph_distance', -1))
        
        # 12. payer_account_age_days
        payer_age = float(tx.get('payer_account_age_days', 0))
        
        # 13. device_match (1 if same device as usual)
        device_match = 1 if tx.get('device_match') else 0
        
        # 14. is_new_payee
        is_new_payee = 1 if tx.get('is_new_payee') else 0
        
        # 15. payee_blacklist_score
        blacklist_score = float(tx.get('payee_blacklist_score', 0.0))
        
        # 16. amount_round_number (1 if round number like 5000)
        # We consider multiples of 100 or 500 as round numbers
        is_round = 1 if amount > 0 and (amount % 100 == 0) else 0
        
        # 17. is_high_value (1 if amount > 10000)
        is_high_value = 1 if amount > 10000 else 0
        
        # 18. hour_of_day
        # Calculated above
        
        return np.array([
            upi_age_days,
            registration_state_risk,
            tx_velocity_1hr,
            tx_velocity_24hr,
            tx_velocity_7d,
            amount,
            amount_deviation,
            time_of_day_risk,
            is_weekend,
            is_post_call,
            graph_dist,
            payer_age,
            device_match,
            is_new_payee,
            blacklist_score,
            is_round,
            is_high_value,
            float(hour)
        ], dtype=np.float32)
