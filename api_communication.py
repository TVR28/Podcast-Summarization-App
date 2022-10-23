import requests
import json
import time
from api_secrets import API_KEY_ASSEMBLYAI, API_KEY_LISTENNOTES
import pprint

from listennotes import podcast_api

transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'
headers_assemblyai = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

listennotes_episode_endpoint = 'https://listen-api.listennotes.com/api/v2/'
headers_listennotes = {
  'X-ListenAPI-Key': API_KEY_LISTENNOTES,
}


def get_episode_audio_url(episode_id):
    client = podcast_api.Client(api_key=API_KEY_LISTENNOTES)
    response = client.fetch_episode_by_id(
    id=episode_id,
    show_transcript=1,
    )
    data = response.json()


    episode_title = data['title']
    thumbnail = data['thumbnail']
    podcast_title = data['podcast']['title']
    audio_url = data['audio']
    return audio_url, thumbnail, podcast_title, episode_title

def transcribe(audio_url, auto_chapters):
    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': auto_chapters
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers_assemblyai)
    pprint.pprint(transcript_response.json())
    return transcript_response.json()['id']


def poll(transcript_id):
    polling_endpoint = f'{transcript_endpoint}/{transcript_id}'
    polling_response = requests.get(polling_endpoint, headers=headers_assemblyai)
    return polling_response.json()


def get_transcription_result_url(url, auto_chapters):
    transcribe_id = transcribe(url, auto_chapters)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print("waiting for 60 seconds")   #podcasts might be longer
        time.sleep(60)


def save_transcript(episode_id):
    audio_url, thumbnail, podcast_title, episode_title = get_episode_audio_url(episode_id)
    data, error = get_transcription_result_url(audio_url, auto_chapters=True)
    pprint.pprint(data)

    if data:
        filename = f'{episode_id}.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])

        filename = f'{episode_id}_chapters.json'
        with open(filename, 'w') as f:
            chapters = data['chapters']

            data = {'chapters': chapters}
            data['audio_url']=audio_url
            data['thumbnail']=thumbnail
            data['podcast_title']=podcast_title
            data['episode_title']=episode_title
            # for key, value in kwargs.items():
            #     data[key] = value

            json.dump(data, f, indent=4)
            print('Transcript saved')
            return True
    elif error:
        print("There is an Error!!!", error)
        return False