"""
Simple test script to verify API functionality
"""
import asyncio
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_languages():
    """Test languages endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/languages")
        print(f"Languages: {response.status_code}")
        languages = response.json()
        print(f"Found {len(languages)} languages")
        for lang in languages[:5]:  # Show first 5
            print(f"  {lang['code']}: {lang['name']}")
        return response.status_code == 200
    except Exception as e:
        print(f"Languages test failed: {e}")
        return False

def test_translation():
    """Test translation endpoint"""
    try:
        data = {
            "text": "Hello, how are you today?",
            "source_language": "en",
            "target_language": "hi"
        }
        response = requests.post(f"{BASE_URL}/translate", json=data)
        print(f"Translation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Original: {result['original_text']}")
            print(f"Translated: {result['translated_text']}")
            print(f"Confidence: {result.get('confidence_score', 'N/A')}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Translation test failed: {e}")
        return False

def test_language_detection():
    """Test language detection endpoint"""
    try:
        params = {"text": "नमस्ते, आप कैसे हैं?"}
        response = requests.post(f"{BASE_URL}/detect-language", params=params)
        print(f"Language Detection: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Text: {result['text']}")
            print(f"Detected Language: {result['detected_language']}")
            print(f"Language Name: {result['language_name']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Language detection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Multilingual Voice Translation API")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Languages", test_languages),
        ("Translation", test_translation),
        ("Language Detection", test_language_detection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        success = test_func()
        results.append((test_name, success))
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
