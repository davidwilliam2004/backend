import re
import requests
import textwrap
from gtts import gTTS
import os
from django.conf import settings
import os
import re


def clean_text(text):
    """
    Cleans AI-generated text by removing markdown, special characters, and extra spaces.
    pass (str) as argument return as (str)
    """    
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **text**
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # *text*
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)# -.text
    text = re.sub(r"\*", "", text) # *
    text = re.sub(r'\s+', ' ', text).strip()# " "
    return text


def text_to_speech(text, lang="en", filename="output.mp3"):
    """
    Convert text to speech and save as an audio file.
    Parameters:
    - text (str): The text to convert to speech.
    - lang (str): Language code ('en' for English, 'ta' for Tamil).
    - filename (str): Name of the output MP3 file.
    Returns:
    - str: Path to the saved audio file.
    """
    # Ensure media/audio directory exists
    audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    # Create TTS object
    tts = gTTS(text=text, lang=lang)
    file_path = os.path.join(audio_dir, filename)
    tts.save(file_path)
    return file_path



def translate_to_tamil(text, chunk_size=450):
    """
    Translate English text to Tamil using MyMemory API.

    - Automatically splits long texts (500-char limit per request)
    - Handles API errors gracefully
    """
    url = "https://api.mymemory.translated.net/get"
    translated_text = []
    for chunk in textwrap.wrap(text, chunk_size):
        params = {"q": chunk, "langpair": "en|ta"}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            translated_text.append(data.get("responseData", {}).get("translatedText", ""))
        else:
            translated_text.append("Translation failed")

    return " ".join(translated_text)

# def text_to_speech(text ,lang="en", filename=audio_filename):
#     audio_path = os.path.join(settings.MEDIA_ROOT, "audio", audio_filename)
#     os.makedirs(os.path.dirname(audio_path), exist_ok=True)
#     tts = gTTS(text, lang="en")
#     tts.save(audio_path)
