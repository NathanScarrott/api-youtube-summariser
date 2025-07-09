import requests
import json
import os

from fastapi import FastAPI, Request

from youtube_transcript_api import YouTubeTranscriptApi

from pytube import Playlist

from sql_action import get_connection, create_table, insert_summary, fetch_summary, insert_transcript, fetch_summary_by_video_id

from llm import model_request

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/transcript/{video_id}")
def get_video_transcript(video_id:str):
    try:
        transcript_raw = YouTubeTranscriptApi.get_transcript(video_id)

        transcript_list = [transcript["text"] for transcript in transcript_raw]
        result = " ".join(transcript_list)

        connection = get_connection(db_name="summaries.db")
        create_table(connection=connection)
        insert_transcript(connection, transcript=result, videoId=video_id, playlistId = None)

        return {"transcript" : result}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/transcripts/{playlist_id}")
def get_playlist_transcript(playlist_id:str):
    playlist_ids = _get_video_ids_from_playlist(playlist_id)
    transcripts = []

    for video_id in playlist_ids:
        try:
            transcript_raw = YouTubeTranscriptApi.get_transcript(video_id)

            transcript_list = [transcript["text"] for transcript in transcript_raw]
            result = " ".join(transcript_list)

            connection = get_connection(db_name="summaries.db")
            create_table(connection=connection)
            insert_transcript(connection, transcript=result, videoId=video_id, playlistId = playlist_id)

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

def _generate_video_summary(video_id):
    connection = get_connection(db_name="summaries.db")
    create_table(connection=connection)

    rows = fetch_summary_by_video_id(connection, video_id)
    
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
    


                        
    
