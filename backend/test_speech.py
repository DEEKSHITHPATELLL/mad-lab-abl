#!/usr/bin/env python3
"""
Test script for speech-to-text functionality
"""
import requests
import json

def test_speech_to_text():
    """Test the speech-to-text endpoint"""
    
    # Test with a simple text file (simulating audio)
    url = "http://192.168.116.67:8000/api/v1/speech-to-text"
    
    # Create a dummy audio file for testing
    test_data = b"dummy audio data for testing"
    
    files = {
        'audio': ('test.wav', test_data, 'audio/wav')
    }
    
    data = {
        'language': 'en'
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Speech-to-text endpoint is working!")
            print(f"Text: {result.get('text', 'N/A')}")
            print(f"Language: {result.get('language', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://192.168.116.67:8000/api/v1/health")
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection error: {e}")

if __name__ == "__main__":
    print("🔧 Testing Voice Translation Backend...")
    print("\n1. Testing Health Endpoint:")
    test_health()
    
    print("\n2. Testing Speech-to-Text Endpoint:")
    test_speech_to_text()
    
    print("\n✅ Test completed!")
