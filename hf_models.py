# hf_models.py
from transformers import pipeline
import os
from dotenv import load_dotenv

load_dotenv()
DEVICE = 0 if os.getenv("HF_DEVICE") == "cuda" else -1

# Modèles recommandés
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
SENTIMENT_MODEL = "nlptown/bert-base-multilingual-uncased-sentiment"

print("Loading HF pipelines (this may take time)...")
emotion_pipe = pipeline("text-classification", model=EMOTION_MODEL, device=DEVICE)
sentiment_pipe = pipeline("sentiment-analysis", model=SENTIMENT_MODEL, device=DEVICE)
print("Pipelines loaded.")

def detect_emotion(text):
    """Retourne (emotion_label, score)"""
    if not text or text.strip() == "":
        return {"label": "neutral", "score": 1.0}
    res = emotion_pipe(text, truncation=True)[0]
    return res

def detect_sentiment(text):
    res = sentiment_pipe(text, truncation=True)[0]
    return res

def detect_cognitive_overload(text, recent_activity=None):
    """
    Heuristique simple pour surcharge cognitive
    """
    text_low = (text or "").lower()
    keywords = ["overwhelmed", "overwhelm", "tired", "confused", "lost", "perdu", "stress", "anxious", "anxiété", "fatigué"]
    hits = sum(1 for k in keywords if k in text_low)
    score = min(1.0, hits / 3.0)
    
    if recent_activity and recent_activity.get("avg_score") is not None:
        avg = recent_activity["avg_score"]
        if avg < 0.6:
            score = min(1.0, score + (0.6 - avg))
    
    overloaded = score > 0.3
    return {"overloaded": overloaded, "score": score}