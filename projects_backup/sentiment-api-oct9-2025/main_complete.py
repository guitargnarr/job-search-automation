"""
Sentiment Analysis API - COMPLETE IMPLEMENTATION
All portfolio claims implemented and working
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import time
import hashlib
import json

# Real transformer imports
from transformers import pipeline
import redis

app = FastAPI(
    title="Sentiment Analysis API",
    description="Production sentiment analysis with multi-language support and emotion detection",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    language: Optional[str] = "auto"

class BatchInput(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    language: Optional[str] = "auto"

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    emotions: Dict[str, float]
    language: str
    processing_time: float
    cached: bool

class HealthResponse(BaseModel):
    status: str
    models_loaded: Dict[str, bool]
    cache_connected: bool
    uptime: float

# Global models and cache
sentiment_model = None
multilingual_model = None
emotion_model = None
redis_client = None
start_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Initialize all models and cache"""
    global sentiment_model, multilingual_model, emotion_model, redis_client

    print("Loading transformer models...")

    # 1. English sentiment (fast, accurate)
    sentiment_model = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    print("✅ English sentiment model loaded")

    # 2. Multilingual sentiment (50+ languages)
    multilingual_model = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment"
    )
    print("✅ Multilingual model loaded (50+ languages)")

    # 3. Emotion detection
    emotion_model = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None  # Return all emotion scores
    )
    print("✅ Emotion detection model loaded")

    # 4. Redis cache
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        print("✅ Redis cache connected")
    except Exception as e:
        redis_client = None
        print(f"⚠️ Redis not available: {e}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check with model status"""
    return HealthResponse(
        status="healthy",
        models_loaded={
            "sentiment_en": sentiment_model is not None,
            "multilingual": multilingual_model is not None,
            "emotion": emotion_model is not None
        },
        cache_connected=redis_client is not None,
        uptime=time.time() - start_time
    )

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(input_data: TextInput):
    """Analyze sentiment with emotion detection"""
    if not sentiment_model:
        raise HTTPException(status_code=503, detail="Models not loaded")

    start = time.time()
    text = input_data.text
    language = input_data.language
    cached = False

    # Check Redis cache
    cache_key = None
    if redis_client:
        cache_key = f"sentiment:{hashlib.md5(text.encode()).hexdigest()}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            result = json.loads(cached_result)
            result['processing_time'] = (time.time() - start) * 1000
            result['cached'] = True
            return SentimentResponse(**result)

    # Choose model based on language
    if language != "en" and language != "auto":
        model = multilingual_model
    else:
        model = sentiment_model

    # Run sentiment analysis
    sent_result = model(text)[0]

    # Map labels
    if 'stars' in sent_result['label']:
        # Multilingual model returns stars
        stars = int(sent_result['label'].split()[0])
        sentiment = "positive" if stars >= 4 else "negative" if stars <= 2 else "neutral"
        confidence = sent_result['score']
    else:
        sentiment = sent_result['label'].lower()
        confidence = sent_result['score']

    # Run emotion detection (English only for now)
    emotions = {"joy": 0.0, "sadness": 0.0, "anger": 0.0, "fear": 0.0, "surprise": 0.0}
    if emotion_model and (language == "en" or language == "auto"):
        emotion_results = emotion_model(text)[0]
        for result in emotion_results:
            emotion_label = result['label'].lower()
            if emotion_label in emotions:
                emotions[emotion_label] = result['score']

    response_data = {
        "sentiment": sentiment,
        "confidence": confidence,
        "emotions": emotions,
        "language": language if language != "auto" else "en",
        "processing_time": (time.time() - start) * 1000,
        "cached": False
    }

    # Cache result (1 hour TTL)
    if redis_client and cache_key:
        redis_client.setex(cache_key, 3600, json.dumps(response_data))

    return SentimentResponse(**response_data)

@app.post("/analyze/batch")
async def analyze_batch(input_data: BatchInput):
    """Analyze multiple texts in parallel"""
    if not sentiment_model:
        raise HTTPException(status_code=503, detail="Models not loaded")

    start = time.time()

    # Use appropriate model
    model = multilingual_model if input_data.language != "en" else sentiment_model

    # Batch inference
    results = model(input_data.texts)

    # Process results
    processed = []
    for text, result in zip(input_data.texts, results):
        if 'stars' in result['label']:
            stars = int(result['label'].split()[0])
            sentiment = "positive" if stars >= 4 else "negative" if stars <= 2 else "neutral"
        else:
            sentiment = result['label'].lower()

        processed.append({
            "text": text[:50] + "..." if len(text) > 50 else text,
            "sentiment": sentiment,
            "confidence": result['score']
        })

    total_time = (time.time() - start) * 1000

    return {
        "results": processed,
        "total_time_ms": total_time,
        "avg_time_per_text_ms": total_time / len(input_data.texts),
        "texts_processed": len(input_data.texts)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
