#!/usr/bin/env python3
"""
Safely inspect the pickle model artifact to understand its structure.
"""

import pickle
import sys

model_path = r"C:\seva_hackthon\model\civicpulse_priority_model.pkl"

try:
    print(f"Loading model from: {model_path}")
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    
    print("\n✓ Model artifact loaded successfully!")
    print(f"Type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"\nDictionary Keys: {list(data.keys())}")
        for key, value in data.items():
            print(f"  - {key}: {type(value).__name__}")
    else:
        print(f"\nObject attributes/methods:")
        attrs = [a for a in dir(data) if not a.startswith('_')]
        for attr in attrs[:20]:  # First 20
            print(f"  - {attr}")
    
    # Check for common model types
    if hasattr(data, 'predict'):
        print("\n✓ Has predict() method - appears to be sklearn/ml model")
    if hasattr(data, 'model'):
        print("✓ Has 'model' attribute")
    if hasattr(data, 'feature_names'):
        print(f"✓ Has feature_names: {data.feature_names}")
    if hasattr(data, 'classes_'):
        print(f"✓ Has classes_: {data.classes_}")
    if hasattr(data, 'n_features_in_'):
        print(f"✓ Expects {data.n_features_in_} input features")
    
except Exception as e:
    print(f"✗ Error loading model: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
