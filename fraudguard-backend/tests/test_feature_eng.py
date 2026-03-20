import pytest
import numpy as np
import time
from datetime import datetime
from app.ml.feature_eng import FeatureExtractor

@pytest.fixture
def extractor():
    return FeatureExtractor()

def test_feature_extraction_values(extractor):
    # Test dictionary setup
    tx = {
        'upi_age_days': 10,
        'registration_state_risk': 0.1,
        'tx_velocity_1hr': 2,
        'tx_velocity_24hr': 5,
        'tx_velocity_7d': 15,
        'amount': 5000,
        'amount_deviation_from_user_baseline': 1500,
        'timestamp': datetime(2024, 10, 5, 23, 0), # 11 PM, Saturday (is_weekend=1)
        'is_post_call': True,
        'payee_payer_graph_distance': 3,
        'payer_account_age_days': 100,
        'device_match': 1,
        'is_new_payee': 0,
        'payee_blacklist_score': 0.05
    }
    
    features = extractor.extract_features(tx)
    
    assert isinstance(features, np.ndarray)
    assert features.shape == (18,)
    
    # Check individual features based on the indices
    # upi_age_days
    assert features[0] == 10
    # registration_state_risk
    assert features[1] == 0.1
    # tx_velocity_1hr
    assert features[2] == 2
    # tx_velocity_24hr
    assert features[3] == 5
    # tx_velocity_7d
    assert features[4] == 15
    # amount
    assert features[5] == 5000
    # amount_deviation_from_user_baseline
    assert features[6] == 1500
    # time_of_day_risk (at 23:00, risk should be around 0.8 according to our lookup)
    assert features[7] == 0.8
    # is_weekend (Oct 5th 2024 is Saturday)
    assert features[8] == 1
    # is_post_call
    assert features[9] == 1
    # payee_payer_graph_distance
    assert features[10] == 3
    # payer_account_age_days
    assert features[11] == 100
    # device_match
    assert features[12] == 1
    # is_new_payee
    assert features[13] == 0
    # payee_blacklist_score
    assert features[14] == 0.05
    # amount_round_number (5000 is round)
    assert features[15] == 1
    # is_high_value (5000 < 10000)
    assert features[16] == 0
    # hour_of_day
    assert features[17] == 23

def test_feature_high_value_and_round(extractor):
    # Test high value and non-round amount
    tx_high = {
        'amount': 15000.5,
        'timestamp': datetime(2024, 10, 4, 10, 0) # 10 AM, Friday
    }
    features = extractor.extract_features(tx_high)
    # amount
    assert features[5] == 15000.5
    # is_round (15000.5 is not multiple of 100)
    assert features[15] == 0
    # is_high_value (> 10000)
    assert features[16] == 1
    # is_weekend (Friday)
    assert features[8] == 0

def test_performance(extractor):
    tx = {
        'upi_age_days': 100,
        'registration_state_risk': 0.1,
        'tx_velocity_1hr': 2,
        'amount': 500,
        'timestamp': datetime.now()
    }
    
    # Warmup
    for _ in range(100):
        extractor.extract_features(tx)
        
    start_time = time.perf_counter()
    n_calls = 1000
    for _ in range(n_calls):
        extractor.extract_features(tx)
    end_time = time.perf_counter()
    
    avg_time = (end_time - start_time) / n_calls
    avg_time_ms = avg_time * 1000
    
    print(f"\nAverage processing time per call: {avg_time_ms:.4f} ms")
    assert avg_time_ms < 5, f"Performance requirement failed: {avg_time_ms:.4f} ms"

def test_missing_fields(extractor):
    # Test with empty dict to check defaults
    tx = {}
    features = extractor.extract_features(tx)
    assert features.shape == (18,)
    # Defaults should be zeros or sensible values
    assert features[0] == 0 # upi_age_days
    assert features[5] == 0 # amount
    assert features[10] == -1 # graph_distance (default in our implementation)
