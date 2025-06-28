from google import genai
from google.genai import types
import wave
import concurrent.futures
from dotenv import load_dotenv
import os

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)


def generate_single_tts(client, story_id, page_text, page_num):
    """Generate TTS for a single page"""
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=page_text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name='Kore',
                )
            ),
            )
        )
    )

    data = response.candidates[0].content.parts[0].inline_data.data
    file_name = f'{story_id}_{page_num}.wav'
    wave_file(file_name, data)
    print(f"tts saved for page {page_num}")


def generate_tts(story_id, pages):
    load_dotenv() 
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i, page in enumerate(pages):
            future = executor.submit(generate_single_tts, client, story_id, page, i+1)
            futures.append(future)
        
        concurrent.futures.wait(futures)