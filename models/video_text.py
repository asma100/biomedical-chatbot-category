import yt_dlp
import requests
import time

# AssemblyAI API key
api_key = 'your_assemblyai_api_key'

# Step 1: Download Audio from YouTube
def download_audio_from_youtube(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio.mp3',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    print("Audio downloaded successfully.")
    return 'audio.mp3'

# Step 2: Upload Audio to AssemblyAI
def upload_audio_to_assemblyai(file_path):
    headers = {'authorization': api_key}
    with open(file_path, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload',
                                 headers=headers, files={'file': f})
    upload_url = response.json()['upload_url']
    print(f"File uploaded to: {upload_url}")
    return upload_url

# Step 3: Submit Audio for Transcription
def transcribe_audio(upload_url):
    headers = {'authorization': api_key}
    transcript_request = {'audio_url': upload_url, 'language_code': 'en'}
    
    transcript_response = requests.post('https://api.assemblyai.com/v2/transcript',
                                        json=transcript_request, headers=headers)
    transcript_id = transcript_response.json()['id']
    print(f"Transcription ID: {transcript_id}")
    return transcript_id

# Step 4: Poll for Transcription Completion
def get_transcription_result(transcript_id):
    headers = {'authorization': api_key}
    transcript_status_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'

    while True:
        status_response = requests.get(transcript_status_url, headers=headers)
        status = status_response.json()['status']

        if status == 'completed':
            print("Transcription complete.")
            return status_response.json()['text']
        elif status == 'failed':
            print("Transcription failed.")
            return None
        else:
            print("Transcription in progress...")
            time.sleep(5)

# Complete Process
youtube_url = "https://www.youtube.com/watch?v=VIDEO_ID"  # Replace with actual video URL
audio_file = download_audio_from_youtube(youtube_url)
upload_url = upload_audio_to_assemblyai(audio_file)
transcript_id = transcribe_audio(upload_url)
transcript_text = get_transcription_result(transcript_id)

if transcript_text:
    print("Transcribed Text:\n", transcript_text)
