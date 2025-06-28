import re
import types
from google import genai
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO


def extract_pages(response_text):
    pages = []
    descriptions = []
    lines = response_text.split('\n')
    
    for line in lines:
        match = re.match(r'Page\s+(\d+):\s*(.*)', line.strip(), re.IGNORECASE)
        if match:
            page_num = int(match.group(1))
            page_text = match.group(2).strip()
            while len(pages) < page_num:
                pages.append("")
            pages[page_num - 1] = page_text

        desc_match = re.match(r'Page\s+(\d+)\s+Desc:\s*(.*)', line.strip(), re.IGNORECASE)
        if desc_match:
            page_num = int(desc_match.group(1))
            desc_text = desc_match.group(2).strip()
            while len(descriptions) < page_num:
                descriptions.append("")
            descriptions[page_num - 1] = desc_text
    
    return pages, descriptions

def generate_story(story_id, query):
    load_dotenv() 
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # query = "Tell me a story about a knight who goes on an adventure."

    story_prompt = f'''
    You are a Storyteller AI that helps write children's stories.
    You will be given a story prompt and you will write a story based on that prompt.
    The story should be simple for children. 1-2 sentences per page.
    The story should be 5 pages long.
    Be more creative with character names and places.

    Also, generate detailed descriptions of the scene, including detailed character visual descriptions and the scene.
    Keep the character descriptions consistent across pages.

    Please format your output as follows:

    Page 1: Text
    Page 1 Desc:
    Page 2: Text
    Page 2 Desc:
    Page 3: Text
    Page 3 Desc:
    Page 4: Text
    Page 4 Desc:
    Page 5: Text
    Page 5 Desc:

    Story prompt: {query}
    '''

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=story_prompt
    )

    chat = client.chats.create(
        model="gemini-2.0-flash-preview-image-generation",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    image_prompt ='''
    Generate an image of the following page text and description.
    This is for a children's book illustration, so it should be colorful and engaging.
    Make the style watercolor, with a whimsical and playful feel.
    Do not include the page text in the image, I will add it after.
    If this is not the first image generated in the conversation, keep the style consistent with previous images.
    Be sure to actually include what is in the description of the image. Do not make things up or add new things.
    Do NOT include ANY text in the image.

    The image must have an aspect ratio of 1:1 (square)


    Page Text: {current_page}
    Page Description: {current_desc}
    '''

    story_pages, descriptions = extract_pages(response.text)
    for i, (page, desc) in enumerate(zip(story_pages, descriptions)):
        response = chat.send_message(
            image_prompt.format(current_page=page, current_desc=desc),
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                import base64
                try:
                    if part.inline_data.mime_type.startswith("image/"):
                        image_data = base64.b64decode(part.inline_data.data)
                        image = Image.open(BytesIO(image_data))
                        image.save(f'{story_id}{i}.png')
                    else:
                        print(f"Unexpected mime type: {part.inline_data.mime_type}")
                except Exception as e:
                    print(f"Failed to process image for page {i + 1}: {e}")