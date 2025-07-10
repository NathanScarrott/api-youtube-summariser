import os
from typing import List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import requests

from sql_action import (
    get_connection, 
    create_table, 
    insert_summary, 
    insert_transcript, 
    fetch_data_by_video_id, 
    insert_favourite, 
    create_favourites_table
)
from llm import model_request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YouTube Summarizer API", version="1.0.0")

# Request models
class VideoRequest(BaseModel):
    video_id: str


@app.get("/transcript/{video_id}")
def get_transcript(video_id: str) -> Dict[str, Any]:
    """Get and store transcript for a single video."""
    try:
        transcript = _get_transcript_from_video_id(video_id)
        return {"transcript": transcript}
    except Exception as e:
        return {"error": str(e)}


@app.get("/transcripts/{playlist_id}")
def get_playlist_transcripts(playlist_id: str) -> Dict[str, Any]:
    """Get transcripts for all videos in a playlist."""
    try:
        video_ids = _get_video_ids_from_playlist(playlist_id)
        transcripts = []

        for video_id in video_ids:
            try:
                transcript = _get_transcript_from_video_id(video_id)
                transcripts.append({"video_id": video_id, "transcript": transcript})
            except Exception as e:
                print(f"Error processing video {video_id}: {e}")
                transcripts.append({"video_id": video_id, "error": str(e)})
        
        return {"transcripts": transcripts}
    except Exception as e:
        return {"error": str(e)}


@app.get("/summary/{video_id}")
def get_summary(video_id: str) -> Dict[str, Any]:
    """Generate summary for a video from stored transcript."""
    try:
        summary = _generate_video_summary(video_id)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}


@app.get("/summaries/{playlist_id}")
def get_playlist_summaries(playlist_id: str) -> Dict[str, Any]:
    """Generate summaries for all videos in a playlist."""
    try:
        summaries = []
        video_ids = _get_video_ids_from_playlist(playlist_id)
        
        for video_id in video_ids:
            try:
                summary = _generate_video_summary(video_id)
                summaries.append({"video_id": video_id, "summary": summary})

                # Store summary in database
                connection = get_connection("summaries.db")
                create_table(connection)
                insert_summary(connection, summary, video_id, playlist_id)
                connection.close()
                
            except Exception as e:
                print(f"Error processing video {video_id}: {e}")
                summaries.append({"video_id": video_id, "error": str(e)})

        return {"summaries": summaries}
    except Exception as e:
        return {"error": str(e)}


@app.get("/retrieve-summary/{video_id}")
def retrieve_stored_summary(video_id: str) -> Dict[str, Any]:
    """Retrieve a previously stored summary."""
    try:
        connection = get_connection("summaries.db")
        create_table(connection)
        rows = fetch_data_by_video_id(connection, video_id)
        connection.close()

        if not rows:
            return {"error": "No summary found for this video"}
        
        summary = rows[0][1]  # summary column
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}


@app.get("/retrieve-transcript/{video_id}")
def retrieve_stored_transcript(video_id: str) -> Dict[str, Any]:
    """Retrieve a previously stored transcript."""
    try:
        connection = get_connection("summaries.db")
        create_table(connection)
        rows = fetch_data_by_video_id(connection, video_id)
        connection.close()

        if not rows:
            return {"error": "No transcript found for this video"}
        
        transcript = rows[0][4]  # transcript column
        return {"transcript": transcript}
    except Exception as e:
        return {"error": str(e)}


@app.post("/favourites")
def add_to_favourites(request: VideoRequest) -> Dict[str, str]:
    """Add a video to favourites."""
    try:
        connection = get_connection("summaries.db")
        create_table(connection)
        rows = fetch_data_by_video_id(connection, request.video_id)
        connection.close()

        if not rows:
            return {"error": f"No summary found for video {request.video_id}"}

        video_id = rows[0][2]  # videoId column
        summary = rows[0][1]   # summary column

        # Store in favourites
        favourites_connection = get_connection("favourites.db")
        create_favourites_table(favourites_connection)
        insert_favourite(favourites_connection, video_id, summary)
        favourites_connection.close()

        return {"message": f"Video {video_id} added to favourites"}
    except Exception as e:
        return {"error": str(e)}


# Helper functions
def _generate_video_summary(video_id: str) -> str:
    """Generate a summary from stored transcript."""
    connection = get_connection("summaries.db")
    create_table(connection)
    rows = fetch_data_by_video_id(connection, video_id)
    connection.close()
    
    if not rows:
        raise Exception(f"No transcript found for video {video_id}")
    
    transcript = rows[0][4]  # transcript column

    prompt = f"""
    Analyze the following transcript from a YouTube video and generate a summary:

    <transcript>
    {transcript}
    </transcript>

    Proceed with the summary without any leading phrases such as "Here is a summary of ...".
    """

    return model_request(prompt)


def _get_video_ids_from_playlist(playlist_id: str) -> List[str]:
    """Get all video IDs from a YouTube playlist."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise Exception("YouTube API key not found in environment variables")
    
    url = f"https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch playlist: {response.status_code}")
    
    response_data = response.json()
    return [item["contentDetails"]["videoId"] for item in response_data["items"]]


def _get_transcript_from_video_id(video_id: str) -> str:
    """Get transcript for a video and store it in database."""
    transcript_raw = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_list = [transcript["text"] for transcript in transcript_raw]
    result = " ".join(transcript_list)

    # Store transcript in database
    connection = get_connection("summaries.db")
    create_table(connection)
    insert_transcript(connection, result, video_id, None)
    connection.close()

    return result
    



                        
    
