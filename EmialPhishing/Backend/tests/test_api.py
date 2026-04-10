import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health check returns correct status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime" in data
        assert "timestamp" in data


class TestModelInfo:
    """Test model info endpoint."""
    
    def test_model_info(self):
        """Test model info returns correct information."""
        response = client.get("/api/v1/model-info")
        assert response.status_code == 200
        
        data = response.json()
        assert "model_name" in data
        assert "max_length" in data
        assert "device" in data
        assert "model_loaded" in data
        assert "tokenizer_loaded" in data
        assert "cache_dir" in data


class TestEmailAnalysis:
    """Test email analysis endpoint."""
    
    def test_analyze_phishing_email(self):
        """Test analysis of phishing email."""
        phishing_email = """
        Subject: URGENT: Your Account Will Be Suspended
        
        Dear User,
        
        Your account will be suspended unless you click here: http://bit.ly/suspicious-link
        
        Act now!
        """
        
        response = client.post(
            "/api/v1/analyze-email",
            json={"email_text": phishing_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "final_decision" in data
        assert "confidence" in data
        assert "stage" in data
        assert "reason" in data
        assert "ml_analysis" in data
        assert "osint_analysis" in data
        
        # Check ML analysis structure
        ml_analysis = data["ml_analysis"]
        assert "prediction" in ml_analysis
        assert "confidence" in ml_analysis
        assert "probabilities" in ml_analysis
        
        # Check OSINT analysis structure
        osint_analysis = data["osint_analysis"]
        assert "risk_score" in osint_analysis
        assert "url_count" in osint_analysis
        assert "email_count" in osint_analysis
        assert "phone_count" in osint_analysis
        assert "suspicious_urls" in osint_analysis
        assert "reasons" in osint_analysis
    
    def test_analyze_safe_email(self):
        """Test analysis of safe email."""
        safe_email = """
        Subject: Team Meeting Tomorrow
        
        Hi everyone,
        
        Just a reminder about our meeting tomorrow at 10 AM.
        
        Thanks,
        John
        """
        
        response = client.post(
            "/api/v1/analyze-email",
            json={"email_text": safe_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["final_decision"] in ["Phishing", "Legitimate"]
        assert 0 <= data["confidence"] <= 1
        assert data["stage"] in ["OSINT", "ML", "Hybrid"]
    
    def test_analyze_email_with_headers(self):
        """Test analysis with email headers."""
        email_text = "Test email content"
        headers = {
            "from": "test@example.com",
            "spf": "pass",
            "dkim": "pass",
            "dmarc": "pass"
        }
        
        response = client.post(
            "/api/v1/analyze-email",
            json={
                "email_text": email_text,
                "headers": headers
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "final_decision" in data
    
    def test_empty_email_text(self):
        """Test analysis with empty email text."""
        response = client.post(
            "/api/v1/analyze-email",
            json={"email_text": ""}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_email_text(self):
        """Test analysis without email text."""
        response = client.post(
            "/api/v1/analyze-email",
            json={}
        )
        
        assert response.status_code == 422  # Validation error


class TestThresholds:
    """Test thresholds endpoints."""
    
    def test_get_thresholds(self):
        """Test getting current thresholds."""
        response = client.get("/api/v1/thresholds")
        assert response.status_code == 200
        
        data = response.json()
        assert "osint_weight" in data
        assert "ml_weight" in data
        assert "high_risk_threshold" in data
        assert "low_risk_threshold" in data
        
        # Validate ranges
        assert 0 <= data["osint_weight"] <= 1
        assert 0 <= data["ml_weight"] <= 1
        assert 0 <= data["high_risk_threshold"] <= 1
        assert 0 <= data["low_risk_threshold"] <= 1
    
    def test_update_thresholds(self):
        """Test updating thresholds."""
        new_thresholds = {
            "osint_weight": 0.4,
            "ml_weight": 0.6,
            "high_risk_threshold": 0.75,
            "low_risk_threshold": 0.25
        }
        
        response = client.put("/api/v1/thresholds", json=new_thresholds)
        assert response.status_code == 200
        
        data = response.json()
        assert data["osint_weight"] == 0.4
        assert data["ml_weight"] == 0.6
        assert data["high_risk_threshold"] == 0.75
        assert data["low_risk_threshold"] == 0.25
    
    def test_invalid_thresholds(self):
        """Test updating with invalid thresholds."""
        invalid_thresholds = {
            "osint_weight": 1.5,  # Invalid: > 1
            "ml_weight": -0.1      # Invalid: < 0
        }
        
        response = client.put("/api/v1/thresholds", json=invalid_thresholds)
        assert response.status_code == 422  # Validation error


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns basic info."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Phishing Detection API"
        assert "version" in data
        assert "status" in data
        assert "docs" in data
        assert "health" in data


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_endpoint(self):
        """Test 404 for non-existent endpoint."""
        response = client.get("/api/v1/non-existent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/v1/analyze-email",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])
