#!/usr/bin/env python3
"""
Example requests for the Phishing Detection API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Example emails for testing
PHISHING_EMAIL = """
Subject: Urgent: Your Account Will Be Suspended

Dear User,

We have detected unusual activity on your account. Your account will be suspended within 24 hours unless you verify your information.

Please click here immediately to verify your account: http://bit.ly/verify-now-urgent

This is your final warning. Failure to comply will result in permanent account closure.

Best regards,
Security Team
"""

SAFE_EMAIL = """
Subject: Team Meeting Tomorrow

Hi everyone,

Just a reminder that we have our weekly team meeting tomorrow at 10 AM in Conference Room B.

Agenda:
1. Project updates
2. Q2 planning
3. Team feedback

Please come prepared with your status reports.

Thanks,
John
"""

PHISHING_WITH_URLS = """
CONGRATULATIONS! YOU'VE WON $1,000,000!!!

You are our lucky winner! Claim your prize now at:
http://www.claim-prize-now.tk
http://tinyurl.com/winner123

Hurry! This offer expires in 24 hours!

Click here: http://suspicious-domain.click/claim
"""

SAFE_WITH_URLS = """
Check out these interesting articles:

1. https://www.nytimes.com/2024/01/01/technology/ai-trends.html
2. https://github.com/microsoft/vscode
3. https://stackoverflow.com/questions/123456/how-to-code

Let me know what you think!

Best,
Sarah
"""


def test_health_check():
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_model_info():
    """Test model info endpoint."""
    print("Testing model info...")
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_analyze_email(email_text, description, headers=None):
    """Test email analysis endpoint."""
    print(f"Testing: {description}")
    print("-" * 50)
    
    payload = {
        "email_text": email_text
    }
    
    if headers:
        payload["headers"] = headers
    
    response = requests.post(f"{BASE_URL}/analyze-email", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Final Decision: {result['final_decision']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Stage: {result['stage']}")
        print(f"Reason: {result['reason']}")
        print(f"ML Confidence: {result['ml_analysis']['confidence']:.2f}")
        print(f"OSINT Risk Score: {result['osint_analysis']['risk_score']:.2f}")
        print(f"Suspicious URLs: {result['osint_analysis']['suspicious_urls']}")
        print(f"Spam Indicators: {result['osint_analysis']['spam_indicators']}")
    else:
        print(f"Error: {response.text}")
    
    print()


def test_train_model():
    """Test model training endpoint."""
    print("Testing model training...")
    payload = {
        "epochs": 2,
        "batch_size": 8
    }
    
    response = requests.post(f"{BASE_URL}/train-model", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_thresholds():
    """Test thresholds endpoints."""
    print("Testing thresholds...")
    
    # Get current thresholds
    response = requests.get(f"{BASE_URL}/thresholds")
    print(f"Current thresholds: {json.dumps(response.json(), indent=2)}")
    
    # Update thresholds
    new_thresholds = {
        "osint_weight": 0.4,
        "ml_weight": 0.6,
        "high_risk_threshold": 0.75
    }
    
    response = requests.put(f"{BASE_URL}/thresholds", json=new_thresholds)
    print(f"Updated thresholds: {json.dumps(response.json(), indent=2)}")
    print()


def main():
    """Run all example tests."""
    print("Phishing Detection API - Example Requests")
    print("=" * 50)
    print()
    
    try:
        # Basic health checks
        test_health_check()
        test_model_info()
        
        # Test email analysis
        test_analyze_email(PHISHING_EMAIL, "Phishing Email - Urgent Account Suspension")
        test_analyze_email(SAFE_EMAIL, "Safe Email - Team Meeting")
        test_analyze_email(PHISHING_WITH_URLS, "Phishing Email - Lottery with Suspicious URLs")
        test_analyze_email(SAFE_WITH_URLS, "Safe Email - Legitimate URLs")
        
        # Test with headers
        headers_example = {
            "from": "security@paypal.com",
            "spf": "fail",
            "dkim": "fail",
            "dmarc": "fail"
        }
        test_analyze_email(PHISHING_EMAIL, "Phishing Email with Failed Headers", headers_example)
        
        # Test thresholds
        test_thresholds()
        
        # Note: Uncomment to test training (this takes a long time)
        # test_train_model()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Start it with: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
