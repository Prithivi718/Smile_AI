import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from pydantic import BaseModel
from typing import Optional

from dotenv import load_dotenv
load_dotenv()
from googleapiclient.discovery import build

# ------------------------ Intent Extractor ------------------------

import re
import spacy
nlp = spacy.load("en_core_web_sm")


class Extract_Query(BaseModel):
    text: str

def extract_search_topic_spacy(text: str) -> str:

    """Extracts the main search topic from user's request."""
    doc = nlp(text)
    # grab the longest noun chunk (often the main topic)
    chunks = [chunk.text for chunk in doc.noun_chunks]
    if chunks:
        return max(chunks, key=len).lower()
    # fallback: strip punctuation
    return re.sub(r'[^\w\s]', '', text).strip().lower()



# Pydantic input schema for StructuredTool
class DetectTone(BaseModel):
    text: str


tone_keywords = {
    "bored": "funny",
    "tired": "energetic",
    "sad": "happy",
    "angry": "calm",
    "happy": "happy",
    "motivated": "motivated",
    "comedy": "comedy",
    "action": "motivated",
    "dramatic": "light-hearted",
    "fun": "fun",
    "excited": "excited",
    "charming": "happy",
    "romantic": "light-hearted",
    "thriller": "fun",
    "educational": "inspiring",
    "spiritual": "calm",
    "motivational": "motivated",
    "inspiring": "motivated",
    "relaxed": "soothing",
    "fear": "light-hearted"
}


def detect_tone_from_keywords(text: str) -> Optional[str]:
    for keyword in tone_keywords.keys():
        if keyword in text.lower():
            return keyword
    return None

# ------------------------ LLM Query search on YouTube ------------------------
class SearchYTInput(BaseModel):
   text: str

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API")
youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY  # <- This avoids OAuth
)


def search_youtube(text, max_results=5):
    request = youtube.search().list(
        q=text,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()

    results = []
    for item in response['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        url = f"https://www.youtube.com/watch?v={video_id}"
        embed_url = f"https://www.youtube.com/embed/{video_id}?start=0"

        results.append({
            "url": url,
            "embed_url": embed_url,
            "title": title,
            "description": description,
        })
    return results

#print(search_youtube("Energetic Tamil Songs"))
