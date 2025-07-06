import requests
import json
import os

from fastapi import FastAPI, Request
from youtube_transcript_api import YouTubeTranscriptApi

import pymysql

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    db='mydatabase',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.get("/captions/{video_id}")
def get_transcript(video_id):
    api_key = os.getenv("API_KEY")
    
    list_url = f"https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={video_id}&key={api_key}"
    response = requests.get(list_url)
    
    if response.status_code == 200:
        caption_data = response.json()
        return caption_data
    else:
        return {"error": f"Failed to fetch captions: {response.status_code}", "details": response.json()}
    

@app.get("/transcript/{video_id}")
def get_transcript_simple(video_id:str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])

        return {"transcript" : text}
    except Exception as e:
        return {"error": str(e)}

