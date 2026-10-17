
"""Shared AI operations for Speaking Practice and Image Comprehension."""

import base64
import json
import os
import re
import wave
from io import BytesIO

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI


MODEL_NAME = "gemini-3.1-flash-lite"

LANGUAGES = {
    "English": "English",
    "Telugu": "Telugu",
    "Hindi": "Hindi",
}

LEVELS = ["Beginner", "Intermediate", "Advanced"]
MAX_RECORDING_SECONDS = 30


def _get_api_key() -> str:
    """Read the Gemini API key from environment variables or Streamlit secrets."""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        raise ValueError(
            "Google API key not found. Set GOOGLE_API_KEY in your environment "
            "or add it to .streamlit/secrets.toml."
        )

    return api_key


def _get_model() -> ChatGoogleGenerativeAI:
    """Create the configured Gemini chat model."""
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=_get_api_key(),
        temperature=0.4,
    )


def _response_text(response) -> str:
    """Convert a LangChain AI response into text."""
    content = response.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return "\n".join(parts).strip()

    return str(content).strip()


def _parse_json(text: str) -> dict:
    """Parse a JSON object, allowing a surrounding Markdown code fence."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("The AI response did not contain a valid JSON object.")

    return json.loads(cleaned[start : end + 1])


def _audio_duration_seconds(audio_bytes: bytes) -> float:
    """Read the duration of a WAV recording without extra dependencies."""
    try:
        with wave.open(BytesIO(audio_bytes), "rb") as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()

            if sample_rate <= 0:
                raise ValueError("Invalid audio sample rate.")

            return frames / sample_rate
    except (wave.Error, EOFError) as exc:
        raise ValueError(
            "The recording could not be read as WAV audio. Please record again."
        ) from exc


def validate_recording(audio_bytes: bytes) -> float:
    """Validate a recording and return its duration."""
    if not audio_bytes:
        raise ValueError("No recording was received.")

    duration = _audio_duration_seconds(audio_bytes)

    if duration <= 0:
        raise ValueError("The recording is empty.")

    if duration > MAX_RECORDING_SECONDS:
        raise ValueError(
            f"Your recording is {duration:.1f} seconds long. "
            f"Please keep it within {MAX_RECORDING_SECONDS} seconds."
        )

    return duration


def _audio_part(audio_bytes: bytes) -> dict:
    """Build an audio content part for Gemini."""
    return {
        "type": "media",
        "mime_type": "audio/wav",
        "data": base64.b64encode(audio_bytes).decode("utf-8"),
    }


def _image_part(image_bytes: bytes, mime_type: str) -> dict:
    """Build an image content part for Gemini."""
    return {
        "type": "media",
        "mime_type": mime_type,
        "data": base64.b64encode(image_bytes).decode("utf-8"),
    }


def generate_reading_paragraph(language: str, level: str) -> str:
    """Generate a new paragraph in the selected language and difficulty."""
    if language not in LANGUAGES:
        raise ValueError("Please select a supported language.")

    if level not in LEVELS:
        raise ValueError("Please select a supported difficulty level.")

    prompt = f"""
You are a language-learning exercise designer.

Write one original paragraph for a learner to read aloud.

Language: {language}
Difficulty: {level}

Requirements:
- Write entirely in {language}, using its normal writing system.
- Beginner: short, common words and simple sentences.
- Intermediate: everyday vocabulary and connected sentences.
- Advanced: richer vocabulary and varied sentence structures.
- Make it suitable for reading aloud in about 20–30 seconds.
- Use approximately 40–65 words, adjusting naturally for the language.
- Return only the paragraph, without a title, translation, or explanation.
"""

    paragraph = _response_text(_get_model().invoke(prompt))

    if not paragraph:
        raise ValueError("Gemini returned an empty paragraph. Please try again.")

    return paragraph


def evaluate_speaking(
    audio_bytes: bytes,
    language: str,
    reference_paragraph: str,
) -> dict:
    """Transcribe a reading and compare it with the reference paragraph."""
    validate_recording(audio_bytes)

    prompt = f"""
You are evaluating a language learner reading a paragraph aloud.

Expected language: {language}
Reference paragraph:
{reference_paragraph}

Listen to the supplied audio. Transcribe the words actually spoken in
{language}, using its normal writing system.

Compare the transcript with the reference. Be tolerant of minor punctuation
and spelling differences. Do not invent words that cannot be heard.

Return ONLY a JSON object with these keys:
{{
  "transcript": "what the learner said",
  "matching_observations": ["specific words or phrases read correctly"],
  "differences": ["words or phrases that appear omitted, added, or changed"],
  "grammar_feedback": "brief, language-appropriate feedback",
  "improvement_tips": ["one practical tip", "another practical tip"],
  "overall_feedback": "encouraging summary"
}}

All feedback should be written in {language}.
If speech is unclear, say that transcription is uncertain rather than guessing.
Do not provide a numeric pronunciation score. A transcript alone cannot
reliably measure pronunciation.
"""

    message = [
        {"type": "text", "text": prompt},
        _audio_part(audio_bytes),
    ]

    result = _get_model().invoke([("human", message)])
    return _parse_json(_response_text(result))


def evaluate_image_description(
    audio_bytes: bytes,
    image_bytes: bytes,
    image_mime_type: str,
    language: str,
) -> dict:
    """Evaluate a spoken description of an uploaded image."""
    validate_recording(audio_bytes)

    if language not in LANGUAGES:
        raise ValueError("Please select a supported language.")

    prompt = f"""
You are a supportive language tutor evaluating a learner describing an image.

Expected response language: {language}

Study the supplied image and listen to the supplied audio. Transcribe the
learner's description in {language}, using the normal writing system.

Evaluate whether the description mentions details actually visible in the
image. Do not reward invented details as though they were visible.

Return ONLY a JSON object with these keys:
{{
  "transcript": "what the learner said",
  "relevant_details": ["visible details correctly mentioned"],
  "missed_details": ["useful visible details the learner could mention"],
  "unsupported_claims": ["claims not clearly supported by the image"],
  "grammar_feedback": "brief, language-appropriate feedback",
  "improved_description": "a sample description in the selected language",
  "overall_feedback": "encouraging summary"
}}

Write all feedback and the improved description in {language}.
If the audio is unclear, state that transcription is uncertain.
Do not give a numeric pronunciation score.
"""

    message = [
        {"type": "text", "text": prompt},
        _image_part(image_bytes, image_mime_type),
        _audio_part(audio_bytes),
    ]

    result = _get_model().invoke([("human", message)])
    return _parse_json(_response_text(result))
