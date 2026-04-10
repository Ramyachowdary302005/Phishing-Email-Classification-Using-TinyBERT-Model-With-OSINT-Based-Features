#!/usr/bin/env python3
"""
Simple test to check if the API works
"""

import requests
import json

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test email analysis
        print("Testing email analysis...")
        test_email = {
            "email_text": "URGENT: Your account will be suspended. Click here: http://bit.ly/suspicious"
        }
        
        response = requests.post(f"{base_url}/api/v1/analyze-email", json=test_email)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Final Decision: {result['final_decision']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Stage: {result['stage']}")
        else:
            print(f"Error: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
