import sys
import os
sys.path.insert(0, r'c:\Users\DELL\Downloads\programs\multimodal-upi-fraud-detection\backend\src')

try:
    import nlp_detection.impersonation_detector as imp_det
    print("Module loaded successfully")
    print(f"Module contents: {dir(imp_det)}")
    print(f"AUTHORITY_KEYWORDS exists: {'AUTHORITY_KEYWORDS' in dir(imp_det)}")
    print(f"detect_impersonation exists: {'detect_impersonation' in dir(imp_det)}")
except Exception as e:
    print(f"Error loading module: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
