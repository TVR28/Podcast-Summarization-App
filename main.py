import streamlit as st
import glob
import json
import pyttsx3
import base64
from api_communication import save_transcript

text_speech = pyttsx3.init()
voice = text_speech.getProperty('voices')
text_speech.setProperty('voice', voice[1].id)

st.title("PODCAST SUMMARIES")

json_files = glob.glob('*.json')

st.sidebar.markdown('For podcast episodes,Pls visit **_Listen Notes_** website and get the episode id of your favourite podcast by clicking on **_<> Use API to fetch this episode_** and select **_id_** ')
st.sidebar.write("[Go to ListenNotes](https://www.listennotes.com/)")
episode_id = st.sidebar.text_input("Episode ID")
button = st.sidebar.button("Get Episode summary", on_click=save_transcript, args=(episode_id,))

chapters_info = {}


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('bg_1.jpg')

def get_clean_time(start_ms):
    seconds = int((start_ms / 1000) % 60)
    minutes = int((start_ms / (1000 * 60)) % 60)
    hours = int((start_ms / (1000 * 60 * 60)) % 24)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}' if hours > 0 else f'{minutes:02d}:{seconds:02d}'

if button:
    filename = f'{episode_id}_chapters.json'
    print(filename)
    with open(filename, 'r') as f:
        data = json.load(f)

    chapters = data['chapters']
    episode_title = data['episode_title']
    thumbnail = data['thumbnail']
    podcast_title = data['podcast_title']
    audio = data['audio_url']

    st.header(f"{podcast_title} - {episode_title}")
    st.image(thumbnail, width=300)
    st.markdown(f'#### {episode_title}')

    for chp in chapters:
        with st.expander(chp['gist'] + ' - ' + get_clean_time(chp['start'])):
            chp['summary']
