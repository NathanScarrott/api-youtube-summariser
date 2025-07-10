import requests
import json
import os
from pydantic import BaseModel

from fastapi import FastAPI, Request

from youtube_transcript_api import YouTubeTranscriptApi

from pytube import Playlist

from sql_action import get_connection, create_table, insert_summary, fetch_data, insert_transcript, fetch_data_by_video_id, insert_favourite, create_favourites_table

from llm import model_request

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Request model for POST endpoints
class VideoRequest(BaseModel):
    video_id: str

class Transcript(BaseModel):
    transcript: str

class Summary(BaseModel):
    summary: str

@app.get("/generate_transcript/{video_id}")
def generate_transcript(video_id:str):
    try:
        result = _get_transcript_from_video_id(video_id)
        return {"transcript" : result}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/generate_transcripts/{playlist_id}")
def generate_playlist_transcript(playlist_id:str):
    playlist_ids = _get_video_ids_from_playlist(playlist_id)
    transcripts = []

    for video_id in playlist_ids:
        try:
            result = _get_transcript_from_video_id(video_id)
            transcripts.append(result)
        except Exception as e:
            print(f"Error : {str(e)} for ID: {video_id}")
    return {"transcripts": transcripts}

@app.get("/summary/{video_id}")
def generate_video_summary(video_id:str):
    try:
        summary = _generate_video_summary(video_id)
        return {"summary": summary}
    except Exception as e:
        return {"Error": e}
    
@app.get("/summaries/{playlist_id}")
def generate_playlist_summaries(playlist_id:str):
    try:
        summaries = []
        video_ids = _get_video_ids_from_playlist(playlist_id)
        for video_id in video_ids:
            summary = _generate_video_summary(video_id)

            summaries.append(summary)

            connection = get_connection(db_name="summaries.db")
            create_table(connection=connection)
            insert_summary(connection, summary, video_id)

        return {"summaries": summaries}
    except Exception as e:
        return {"Error": e}
    
@app.get("/retrieve-summary/{video_id}")
def retrieve_summary(video_id:str):
    connection = get_connection(db_name="summaries.db")
    create_table(connection=connection)
    rows = fetch_data_by_video_id(video_id)

    if not rows:
        return {"error": "No transcript found for this video"}
    
    summary = rows[0][1]

    return summary

@app.get("/retrieve-transcript/{video_id}")
def retrieve_summary(video_id:str):
    connection = get_connection(db_name="summaries.db")
    create_table(connection=connection)
    rows = fetch_data_by_video_id(video_id)

    if not rows:
        return {"error": "No transcript found for this video"}
    
    transcript = rows[0][4]

    return transcript
    
@app.post("/favourites")
def add_to_favourites(request: VideoRequest):
    try:
        connection = get_connection(db_name="summaries.db")
        create_table(connection=connection)
        rows = fetch_data_by_video_id(connection, request.video_id)

        if not rows:
            return {"error": f"No summary found for video {request.video_id}"}

        video_id = rows[0][2]  # videoId is at index 2
        summary = rows[0][1]   # summary is at index 1

        # Create favourites table and insert
        favourites_connection = get_connection(db_name="favourites.db")
        create_favourites_table(favourites_connection)
        insert_favourite(favourites_connection, video_id, summary)

        return {"message": f"Video {video_id} added to favourites"}
    except Exception as e:
        return {"error": str(e)}


def _generate_video_summary(video_id):
    connection = get_connection(db_name="summaries.db")
    create_table(connection=connection)

    rows = fetch_data_by_video_id(connection, video_id)
    
    if not rows:
        return {"error": "No transcript found for this video"}
    
    transcript = rows[0][4]

    prompt = f"""
    Analayze the following transcript from a youtube video and generate a summary:

    <transcript>
    {transcript}
    </transcript>

    Proceed with the summary wihout any leading phrases such as "Here is a summary of ...".
    """

    summary = model_request(prompt)
    return summary

def _get_video_ids_from_playlist(playlist_id:str):
    api_key = os.getenv("API_KEY")
    
    list_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={api_key}"
    response = requests.get(list_url)

    response_json = response.json()

    ids = [item["contentDetails"]["videoId"] for item in response_json["items"]]

    if response.status_code == 200:
        return ids
    else:
        return {"error": f"Failed to fetch playlist: {response.status_code}", "details": response.json()}
    
def _get_transcript_from_video_id(video_id: str):
    transcript_raw = YouTubeTranscriptApi.get_transcript(video_id)

    transcript_list = [transcript["text"] for transcript in transcript_raw]
    result = " ".join(transcript_list)

    connection = get_connection(db_name="summaries.db")
    create_table(connection=connection)
    insert_transcript(connection, transcript=result, videoId=video_id, playlistId = None)

    return result


    



                        
    
