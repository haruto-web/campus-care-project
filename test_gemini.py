"""
Test Gemini API Connection
Run with: python test_gemini.py
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_care.settings')

import django
django.setup()

from ml_models.gemini_client import GeminiClient

def test_gemini():
    print("Testing Gemini API Connection...\n")
    
    client = GeminiClient()
    
    # Test 1: Risk Prediction
    print("1. Testing Risk Prediction...")
    test_data = {
        'gpa': 2.5,
        'attendance': 70,
        'missing': 3,
        'stress': 4,
        'motivation': 2
    }
    
    try:
        result = client.predict_risk(test_data)
        print("SUCCESS: Risk Prediction works!")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Risk Probability: {result['risk_probability']}")
        print(f"   Risk Factors: {result['risk_factors']}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 2: Sentiment Analysis
    print("\n2. Testing Sentiment Analysis...")
    test_text = "I'm feeling really overwhelmed with all the assignments. I can't keep up."
    
    try:
        result = client.analyze_sentiment(test_text)
        print("SUCCESS: Sentiment Analysis works!")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Alert Level: {result['alert_level']}")
        print(f"   Confidence: {result['confidence']}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 3: Intervention Recommendation
    print("\n3. Testing Intervention Recommendation...")
    test_profile = {
        'risk_level': 'high',
        'issues': 'academic decline, low attendance',
        'year_level': 9
    }
    
    try:
        result = client.recommend_intervention(test_profile)
        print("SUCCESS: Intervention Recommendation works!")
        for rec in result['recommendations']:
            print(f"   - {rec['type']}: {rec['success_probability']:.0%} success")
            print(f"     Reasoning: {rec['reasoning']}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\nAll tests complete!")

if __name__ == '__main__':
    test_gemini()
