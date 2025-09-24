import json
from googleapiclient.discovery import build
import google.generativeai as genai

import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os
import prompts  
import time

load_dotenv()

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set Google Cloud credentials if needed, though often handled by the environment
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('credential_file')

# --- BigQuery Configuration ---
PROJECT_ID = os.getenv("project_id") 
DATASET_ID = os.getenv("dataset_name") 
TABLE_ID = os.getenv("youtube_tbl_name")   

def upload_videos_to_bigquery(videos_list, project_id, dataset_id, table_id):
    if not videos_list:
        print("Video list is empty. No data to upload to BigQuery.")
        return False

    df = pd.DataFrame(videos_list)

    df['published_at'] = pd.to_datetime(df['published_at'])
    df['fetched_at'] = pd.to_datetime(df['fetched_at'])

    expected_columns = [
        'id', 'published_at', 'title', 'url', 'analysis', 
        'fetched_at', 'source', 'channel'
    ]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None
    df = df[expected_columns]

    bq_client = bigquery.Client(project=project_id)
    table_ref = bq_client.dataset(dataset_id).table(table_id)

    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("published_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("analysis", "STRING"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
        bigquery.SchemaField("source", "STRING"),
        bigquery.SchemaField("channel", "STRING"),
    ]

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=schema,
    )

    try:
        print(f"\n[*] Uploading {len(df)} rows to BigQuery table {dataset_id}.{table_id}...")
        job = bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        print(f"[*] Successfully loaded {job.output_rows} rows.")
        return True
    except Exception as e:
        print(f"Error uploading DataFrame to BigQuery: {e}")
        return False

def get_video_details(video_url, GOOGLE_API_KEY):
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content([prompts.youtube_gaming_prompt, video_url])
        
        # Clean the response to ensure it's a valid JSON string
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return cleaned_text
    except Exception as e:
        print(f"Error analyzing video {video_url}: {e}")
        return json.dumps({"error": f"Analysis failed: {str(e)}"})

def get_channel_videos_last_hour(api_key, handle):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        search_response = youtube.search().list(
            q=handle, type="channel", part="snippet", maxResults=1
        ).execute()
        
        if not search_response.get('items'):
            print(f"Channel {handle} not found!")
            return []
        
        channel_id = search_response['items'][0]['snippet']['channelId']
        
        one_hour_ago = datetime.now(pytz.UTC) - timedelta(hours=1)
        one_hour_ago_iso = one_hour_ago.replace(tzinfo=pytz.utc).isoformat()
        
        video_response = youtube.search().list(
            channelId=channel_id,
            publishedAfter=one_hour_ago_iso,
            type="video", part="snippet", maxResults=50, order="date"
        ).execute()
        
        videos = []
        for item in video_response.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'id': item['id']['videoId'],
                'url': f"https://youtu.be/{item['id']['videoId']}",
                'published_at': item['snippet']['publishedAt'],
                'channel': handle
            })
        
        print(f"Found {len(videos)} video(s) from {handle} in the last hour")
        return videos
    except Exception as e:
        print(f"Error processing channel {handle}: {e}")
        return []

def process_multiple_channels(api_key, google_api_key, channel_handles):
    all_videos = []
    
    for handle in channel_handles:
        print(f"\nProcessing channel: {handle}")
        recent_videos = get_channel_videos_last_hour(api_key, handle)
        
        for video in recent_videos:
            print(f"  Analyzing: {video['title'][:50]}...")
            analysis_result = get_video_details(video['url'], google_api_key)
            
            video['analysis'] = analysis_result
            video['fetched_at'] = datetime.now(pytz.UTC)
            video['source'] = 'youtube'
        
        all_videos.extend(recent_videos)
    
    return all_videos

if __name__ == "__main__":
    CHANNEL_HANDLES = ["@MaddenNFLDirect", "@IGN", "@gamespot"] # Example channels
    
    print("🚀 Starting YouTube video processing...")
    
    all_processed_videos = process_multiple_channels(
        YOUTUBE_API_KEY, GOOGLE_API_KEY, CHANNEL_HANDLES
    )
    
    if all_processed_videos:
        print(f"\n🔄 Uploading {len(all_processed_videos)} videos to BigQuery...")
        success = upload_videos_to_bigquery(all_processed_videos, PROJECT_ID, DATASET_ID, TABLE_ID)
        if success:
            print("✅ Successfully uploaded all videos to BigQuery!")
        else:
            print("❌ Failed to upload videos to BigQuery.")
    else:
        print("⚠️  No new videos found to upload.")
    
    print("\n🎉 Processing completed!")

