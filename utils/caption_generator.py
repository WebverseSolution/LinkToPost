import os
import re
from huggingface_hub import InferenceClient
from config import HF_TOKEN  # Loaded from .env or EC2 env vars

# Validate token presence
if not HF_TOKEN:
    raise RuntimeError("❌ HF_TOKEN is not set. Add it to your .env file or EC2 environment.")

# Initialize inference clients
try:
    vision_client = InferenceClient(provider="fireworks-ai", api_key=HF_TOKEN)
    text_client = InferenceClient(api_key=HF_TOKEN)
except Exception as e:
    raise RuntimeError(f"❌ Failed to initialize HuggingFace clients: {e}")


def sanitize_caption(text: str) -> str:
    """Clean and simplify caption output for publishing."""
    text = ''.join(c for c in text if ord(c) <= 0xFFFF)
    text = text.replace('"', '').replace("“", "").replace("”", "").strip()
    note_patterns = [
        r'^note[:\-]', r'^\*', r'^\(.*?\)', r'\[.*?\]', r'^caption:', r'^output:', r'^result:',
        r'^#', r'\b(meta|summary|instruction)\b', r'^text:', r'^\d+\.\s+'
    ]
    for pattern in note_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    return re.sub(r'\s+', ' ', text).strip().strip(".")


def get_detailed_image_description(url: str) -> str:
    """Describe the image in rich detail using a vision-language model."""
    prompt = """
You are a vision assistant. Describe this image with rich detail.
Mention the setting, objects, people, mood, lighting, and visible activity.
Avoid generic or vague responses.
"""
    try:
        completion = vision_client.chat.completions.create(
            model="Qwen/Qwen2-VL-72B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt.strip()},
                        {"type": "image_url", "image_url": {"url": url}},
                    ],
                }
            ],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating image description: {e}"


def generate_emotional_caption(description: str, tone: str = "Emotional", persona: str = "Lifestyle Influencer") -> str:
    """Generate a short emotional caption for an image."""
    prompt = f"""
You are a professional Instagram/Facebook caption writer acting as a {persona}.
Write a short, emotionally resonant caption based on the description below.
Use a {tone.lower()} tone. Avoid literal summaries.
Exclude hashtags, emojis, quotation marks, or meta notes.
Keep the caption under 40 words.

Image Description:
{description}
"""
    try:
        completion = text_client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return sanitize_caption(completion.choices[0].message.content.strip())
    except Exception as e:
        return f"⚠️ Error generating caption: {e}"


def generate_caption_from_text(title: str, description: str, tone: str = "Emotional", persona: str = "Lifestyle Influencer") -> str:
    """Generate a caption from video title and description."""
    prompt = f"""
You are a professional Instagram/Facebook caption writer acting as a {persona}.
Generate a short, expressive caption with emotional appeal for the video below.
Use a {tone.lower()} tone. Avoid literal summaries or explanation.
No emojis, quotation marks, or extra notes. Just a clean, under-40-word caption.

Video Title: {title}
Video Description: {description[:500]}
"""
    try:
        completion = text_client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return sanitize_caption(completion.choices[0].message.content.strip())
    except Exception as e:
        return f"⚠️ Error generating video caption: {e}"


def generate_hashtags(description: str, max_tags: int = 8) -> str:
    """Generate context-aware hashtags from content description."""
    prompt = f"""
From the description below, generate {max_tags} unique and relevant Instagram hashtags.
Avoid generic ones like #love or #happy. Keep them mood- and context-specific.

Description:
{description}
"""
    try:
        response = text_client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return response.choices[0].message.content.strip().replace("\n", " ")
    except Exception as e:
        return f"⚠️ Error generating hashtags: {e}"


def generate_alt_text(description: str) -> str:
    """Generate accessible alt text for screen readers."""
    prompt = f"""
Write a concise and clear alt text for screen readers based on the following description:

{description}
"""
    try:
        response = text_client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating alt text: {e}"
