import os
from typing import Literal

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from prompts.prompt_library import PROMPT_REGISTRY


MODEL_NAME = "gemini-3.1-flash-lite"


# ---------------------------------------------------------------------------
# Pydantic schemas: Grammar Practice
# ---------------------------------------------------------------------------

class GrammarQuestion(BaseModel):
    """One multiple-choice grammar question."""

    id: int = Field(ge=1)
    question: str = Field(min_length=1)
    options: dict[Literal["A", "B", "C", "D"], str]
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str = Field(min_length=1)


class GrammarQuiz(BaseModel):
    """A complete grammar quiz."""

    topic: str = Field(min_length=1)
    level: str = Field(min_length=1)
    questions: list[GrammarQuestion] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Pydantic schemas: Vocabulary Practice
# ---------------------------------------------------------------------------

class VocabularyQuestion(BaseModel):
    """One multiple-choice vocabulary question."""

    id: int = Field(ge=1)
    word: str = Field(min_length=1)
    question: str = Field(min_length=1)
    options: dict[Literal["A", "B", "C", "D"], str]
    correct_answer: Literal["A", "B", "C", "D"]
    definition: str = Field(min_length=1)
    example_sentence: str = Field(min_length=1)
    explanation: str = Field(min_length=1)


class VocabularyQuiz(BaseModel):
    """A complete vocabulary quiz."""

    topic: str = Field(min_length=1)
    level: str = Field(min_length=1)
    questions: list[VocabularyQuestion] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Pydantic schemas: Reading Comprehension and Reading Exam
# ---------------------------------------------------------------------------

class ReadingQuestion(BaseModel):
    """One multiple-choice reading question."""

    id: int = Field(ge=1)
    question: str = Field(min_length=1)
    options: dict[Literal["A", "B", "C", "D"], str]
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str = Field(min_length=1)


class ReadingActivity(BaseModel):
    """A reading passage with its comprehension questions."""

    title: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    level: str = Field(min_length=1)
    passage: str = Field(min_length=1)
    questions: list[ReadingQuestion] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Pydantic schema: Translation Practice
# ---------------------------------------------------------------------------

class TranslationExercise(BaseModel):
    """One sentence for a translation exercise."""

    source_text: str = Field(min_length=1)

class TranslationEvaluation(BaseModel):
    """Evaluation and feedback for a learner's translation."""

    reference_translation: str = Field(min_length=1)
    score: int = Field(ge=0, le=5)
    meaning_feedback: str = Field(min_length=1)
    grammar_feedback: str = Field(min_length=1)
    naturalness_feedback: str = Field(min_length=1)
    improved_translation: str = Field(min_length=1)
    overall_feedback: str = Field(min_length=1)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Read the Google API key from an environment variable or Streamlit secrets."""

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return api_key

    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        raise ValueError(
            "Google API key not found. Add GOOGLE_API_KEY to "
            ".streamlit/secrets.toml or set the GOOGLE_API_KEY environment variable."
        )

    return api_key


def _get_structured_model(schema):
    """Create a Gemini model that returns output matching a Pydantic schema."""

    model = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=_get_api_key(),
        temperature=0.3,
    )
    return model.with_structured_output(schema)


def _to_dict(result, schema) -> dict:
    """Convert structured model output into a validated Python dictionary."""

    if isinstance(result, BaseModel):
        return result.model_dump()

    if isinstance(result, dict):
        return schema.model_validate(result).model_dump()

    raise TypeError(
        f"Unexpected structured output type: {type(result).__name__}"
    )


def _validate_options(questions: list[dict]) -> None:
    """Check that each multiple-choice question has exactly A, B, C and D."""

    expected_labels = {"A", "B", "C", "D"}

    for question in questions:
        if set(question["options"].keys()) != expected_labels:
            raise ValueError(
                f"Question {question['id']} must contain options A, B, C and D."
            )


def _validate_question_count(
    questions: list[dict],
    requested_count: int,
) -> None:
    """Check that the model generated the requested number of questions."""

    if len(questions) != requested_count:
        raise ValueError(
            f"Requested {requested_count} questions, but Gemini returned "
            f"{len(questions)}."
        )

    _validate_options(questions)


def _invoke_structured_prompt(prompt_key: str, schema, inputs: dict):
    """Invoke a registered prompt and validate the structured model response."""

    prompt = PROMPT_REGISTRY[prompt_key]
    chain = prompt | _get_structured_model(schema)
    result = chain.invoke(inputs)
    return _to_dict(result, schema)


# ---------------------------------------------------------------------------
# Grammar Practice
# ---------------------------------------------------------------------------

def generate_grammar_questions(
    topic: str,
    level: str,
    number_of_questions: int = 3,
) -> dict:
    """Generate a validated grammar quiz."""

    if not topic.strip():
        raise ValueError("Grammar topic cannot be empty.")
    if not level.strip():
        raise ValueError("Learner level cannot be empty.")
    if not 1 <= number_of_questions <= 10:
        raise ValueError("number_of_questions must be between 1 and 10.")

    quiz_data = _invoke_structured_prompt(
        "grammar_questions",
        GrammarQuiz,
        {
            "topic": topic,
            "level": level,
            "number_of_questions": number_of_questions,
        },
    )

    _validate_question_count(quiz_data["questions"], number_of_questions)
    return quiz_data


# ---------------------------------------------------------------------------
# Vocabulary Practice
# ---------------------------------------------------------------------------

def generate_vocabulary_questions(
    topic: str,
    level: str,
    number_of_questions: int = 3,
) -> dict:
    """Generate a validated vocabulary quiz."""

    if not topic.strip():
        raise ValueError("Vocabulary topic cannot be empty.")
    if not level.strip():
        raise ValueError("Learner level cannot be empty.")
    if not 1 <= number_of_questions <= 10:
        raise ValueError("number_of_questions must be between 1 and 10.")

    quiz_data = _invoke_structured_prompt(
        "vocabulary_questions",
        VocabularyQuiz,
        {
            "topic": topic,
            "level": level,
            "number_of_questions": number_of_questions,
        },
    )

    _validate_question_count(quiz_data["questions"], number_of_questions)
    return quiz_data


# ---------------------------------------------------------------------------
# Reading Comprehension and Reading Exam
# ---------------------------------------------------------------------------

def _generate_reading_activity(
    prompt_key: str,
    topic: str,
    level: str,
    number_of_questions: int,
) -> dict:
    """Generate and validate a passage and its multiple-choice questions."""

    if not topic.strip():
        raise ValueError("Reading topic cannot be empty.")
    if not level.strip():
        raise ValueError("Learner level cannot be empty.")
    if not 3 <= number_of_questions <= 10:
        raise ValueError("number_of_questions must be between 3 and 10.")

    activity = _invoke_structured_prompt(
        prompt_key,
        ReadingActivity,
        {
            "topic": topic,
            "level": level,
            "number_of_questions": number_of_questions,
        },
    )

    _validate_question_count(activity["questions"], number_of_questions)
    return activity


def generate_reading_comprehension(
    topic: str,
    level: str,
    number_of_questions: int = 3,
) -> dict:
    """Generate a passage and questions for guided reading practice."""

    return _generate_reading_activity(
        "reading_comprehension",
        topic,
        level,
        number_of_questions,
    )


# ---------------------------------------------------------------------------
# Translation Practice
# ---------------------------------------------------------------------------

def generate_translation_exercise(
    source_language: str,
    level: str,
    recent_sentences: list[str] | None = None,
) -> dict:
    """Generate a new source sentence for English translation practice."""

    if not source_language.strip():
        raise ValueError("Select a source language.")

    if source_language == "English":
        raise ValueError("Choose a source language other than English.")

    if not level.strip():
        raise ValueError("Select your learning level.")

    recent_sentences = recent_sentences or []

    exercise = _invoke_structured_prompt(
        "translation_exercise",
        TranslationExercise,
        {
            "source_language": source_language,
            "level": level,
            "recent_sentences": (
                "\n".join(f"- {sentence}" for sentence in recent_sentences)
                or "None yet."
            ),
        },
    )

    return exercise

def evaluate_translation(
    source_text: str,
    source_language: str,
    target_language: str,
    learner_translation: str,
    level: str,
) -> dict:
    """Evaluate a learner's translation and return structured feedback."""

    if not source_text.strip():
        raise ValueError("Source text cannot be empty.")
    if not learner_translation.strip():
        raise ValueError("Please enter your translation.")
    if not source_language.strip() or not target_language.strip():
        raise ValueError("Select both source and target languages.")
    if source_language == target_language:
        raise ValueError("Choose two different languages.")
    if not level.strip():
        raise ValueError("Learner level cannot be empty.")

    return _invoke_structured_prompt(
        "translation_evaluation",
        TranslationEvaluation,
        {
            "source_text": source_text,
            "source_language": source_language,
            "target_language": target_language,
            "learner_translation": learner_translation,
            "level": level,
        },
    )
