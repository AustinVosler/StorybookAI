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
    try:
        print(f"Generating TTS for page {page_num}: {page_text[:50]}...")
        
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

        print(f"Response received for page {page_num}")
        
        if not response.candidates:
            print(f"No candidates in response for page {page_num}")
            return
            
        if not response.candidates[0].content.parts:
            print(f"No parts in response for page {page_num}")
            return

        data = response.candidates[0].content.parts[0].inline_data.data
        os.makedirs("static/audio", exist_ok=True)
        file_name = f'static/audio/{story_id}_{page_num}.wav'
        wave_file(file_name, data)
        print(f"TTS saved for page {page_num}")
        
    except Exception as e:
        print(f"Error generating TTS for page {page_num}: {e}")
        import traceback
        traceback.print_exc()


def generate_tts(story_id, pages):
    print(f"Starting TTS generation for {len(pages)} pages")
    load_dotenv() 
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i, page in enumerate(pages):
            print(f"Submitting page {i+1} for TTS: {page[:30]}...")
            future = executor.submit(generate_single_tts, client, story_id, page, i+1)
            futures.append(future)
        
        print("Waiting for all TTS tasks to complete...")
        concurrent.futures.wait(futures)
        print("All TTS tasks completed")
        
        # Check for any exceptions
        for i, future in enumerate(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Future {i+1} failed: {e}")