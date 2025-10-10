"""
Test suite for Sentiment Analysis API
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check returns expected structure"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data
    assert "cache_connected" in data

def test_sentiment_positive():
    """Test positive sentiment detection"""
    response = client.post("/analyze", json={"text": "I absolutely love this!"})
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert data["confidence"] > 0.9
    assert "emotions" in data

def test_sentiment_negative():
    """Test negative sentiment detection"""
    response = client.post("/analyze", json={"text": "This is terrible and disappointing."})
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "negative"
    assert data["confidence"] > 0.7

def test_batch_processing():
    """Test batch analysis"""
    texts = [
        "Great product!",
        "Terrible experience.",
        "It's okay."
    ]
    response = client.post("/analyze/batch", json={"texts": texts})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3
    assert data["texts_processed"] == 3

def test_emotion_detection():
    """Test emotion scores are returned"""
    response = client.post("/analyze", json={"text": "I'm so excited and happy!"})
    assert response.status_code == 200
    data = response.json()
    assert "emotions" in data
    assert "joy" in data["emotions"]
    assert data["emotions"]["joy"] > 0.5  # Should detect high joy

def test_multilingual_support():
    """Test non-English text"""
    response = client.post("/analyze", json={"text": "¡Esto es maravilloso!", "language": "es"})
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] in ["positive", "negative", "neutral"]

def test_empty_text_validation():
    """Test empty text is rejected"""
    response = client.post("/analyze", json={"text": ""})
    assert response.status_code == 422  # Validation error

def test_batch_size_limit():
    """Test batch size limit enforced"""
    texts = ["Test"] * 101  # Exceeds max of 100
    response = client.post("/analyze/batch", json={"texts": texts})
    assert response.status_code == 422  # Validation error

def test_caching_improves_performance():
    """Test cached requests are faster"""
    text = "This is a test for caching performance"

    # First request (uncached)
    response1 = client.post("/analyze", json={"text": text})
    time1 = response1.json()["processing_time"]

    # Second request (should be cached)
    response2 = client.post("/analyze", json={"text": text})
    time2 = response2.json()["processing_time"]

    # Cached should be faster (if Redis is running)
    if response2.json()["cached"]:
        assert time2 < time1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
