import requests
import json
import os

from fastapi import FastAPI, Request

from youtube_transcript_api import YouTubeTranscriptApi

from pytube import Playlist

from sql_action import get_connection, create_table, insert_summary, fetch_summary

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
        insert_summary(connection, summary=result, videoId=video_id, playlistId = None)

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
            insert_summary(connection, summary=result, videoId=video_id, playlistId = playlist_id)

            transcripts.append(result)
        except Exception as e:
            print(f"Error : {str(e)} for ID: {video_id}")
    return {"transcripts": transcripts}

    
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
    

