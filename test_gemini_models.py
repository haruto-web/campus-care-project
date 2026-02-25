from ml_models.gemini_client import GeminiClient

print("Testing Gemini API...\n")

client = GeminiClient()

# Test 1: Check if 2.5 Flash works (with JSON mode)
print("1. Testing gemini-2.5-flash (JSON mode)...")
try:
    result = client.predict_risk({
        'gpa': 2.5,
        'attendance': 75,
        'missing': 2,
        'stress': 3,
        'motivation': 2
    })
    print("✓ gemini-2.5-flash is WORKING")
    print(f"   Result: {result}")
except Exception as e:
    print(f"✗ gemini-2.5-flash FAILED: {e}")

# Test 2: Check if text generation works
print("\n2. Testing generate_text (fallback to 1.5-flash)...")
try:
    result = client.generate_text("Say 'Hello, I am working!' in one sentence.")
    print("✓ Text generation is WORKING")
    print(f"   Result: {result}")
except Exception as e:
    print(f"✗ Text generation FAILED: {e}")

print("\n✅ Test complete!")
