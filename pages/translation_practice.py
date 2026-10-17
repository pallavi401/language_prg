import streamlit as st

from services.ai_service import (
    evaluate_translation,
    generate_translation_exercise,
)

TARGET_LANGUAGE = "English"

LANGUAGES = [
    "Telugu",
    "Hindi",
    "Tamil",
    "Kannada",
    "Malayalam",
    "Bengali",
    "Marathi",
    "Urdu",
    "Spanish",
    "French",
    "German",
    "Portuguese",
    "Italian",
    "Russian",
    "Japanese",
    "Korean",
    "Chinese",
    "Arabic",
    "Indonesian",
    "Vietnamese",
]

LEVELS = ["Beginner", "Intermediate", "Advanced"]


def _request_new_exercise():
    """Schedule a fresh exercise before the widgets are recreated."""
    st.session_state.translation_generate_pending = True
    st.session_state.translation_feedback = None
    st.session_state.translation_last_request = None
    st.session_state.translation_learner_text = ""


def _generate_exercise_if_pending(source_language, level):
    """Generate an exercise before creating the source-text widget."""

    if not st.session_state.translation_generate_pending:
        return

    recent_sentences = st.session_state.translation_recent_sentences

    try:
        with st.spinner("Generating a new sentence..."):
            exercise = generate_translation_exercise(
                source_language=source_language,
                level=level,
                recent_sentences=recent_sentences[-10:],
            )

        source_text = exercise["source_text"].strip()

        if not source_text:
            raise ValueError("Gemini returned an empty sentence.")

        st.session_state.translation_source_text = source_text

        # Keep a short history to discourage repeated exercises.
        recent_sentences.append(source_text)
        st.session_state.translation_recent_sentences = recent_sentences[-10:]

        st.session_state.translation_generation_error = None

    except Exception as error:
        st.session_state.translation_generation_error = (
            f"{type(error).__name__}: {error}"
        )
        st.session_state.translation_source_text = ""

    finally:
        st.session_state.translation_generate_pending = False


def app():
    # Initialize session state before creating the widgets.
    defaults = {
        "translation_generate_pending": True,
        "translation_recent_sentences": [],
        "translation_feedback": None,
        "translation_last_request": None,
        "translation_source_text": "",
        "translation_learner_text": "",
        "translation_generation_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.header("Translation Practice")
    st.write(
        "Translate an AI-generated sentence into English and receive "
        "feedback on meaning, grammar, and natural phrasing."
    )

    source_language = st.selectbox(
        "Translate from",
        LANGUAGES,
        key="translation_source_language",
        on_change=_request_new_exercise,
    )

    st.text_input(
        "Translate into",
        value=TARGET_LANGUAGE,
        disabled=True,
    )

    level = st.selectbox(
        "Your level",
        LEVELS,
        key="translation_level",
        on_change=_request_new_exercise,
    )

    # Generate before creating the text-area widget. This is important:
    # Streamlit does not allow changing a widget's session-state key
    # after that widget has been instantiated during the current run.
    _generate_exercise_if_pending(source_language, level)

    if st.session_state.translation_generation_error:
        st.error("Could not generate a translation exercise.")
        st.caption(st.session_state.translation_generation_error)

        if st.button("Try Generating Again"):
            _request_new_exercise()
            st.rerun()

        return

    st.caption(
        "Translate the generated sentence into English. "
        "Choose another level or source language for a new exercise."
    )

    source_text = st.text_area(
        f"Source text ({source_language})",
        key="translation_source_text",
        height=110,
    )

    learner_translation = st.text_area(
        "Your translation in English",
        key="translation_learner_text",
        height=140,
        placeholder="Type your English translation here...",
    )

    if st.button("Evaluate Translation", type="primary"):
        if not source_text.strip():
            st.warning("The source sentence is empty. Generate another exercise.")
            return

        if not learner_translation.strip():
            st.warning("Enter your English translation first.")
            return

        try:
            with st.spinner("Reviewing your translation..."):
                feedback = evaluate_translation(
                    source_text=source_text,
                    source_language=source_language,
                    target_language=TARGET_LANGUAGE,
                    learner_translation=learner_translation,
                    level=level,
                )

            st.session_state.translation_feedback = feedback
            st.session_state.translation_last_request = {
                "source_text": source_text,
                "source_language": source_language,
                "target_language": TARGET_LANGUAGE,
                "learner_translation": learner_translation,
                "level": level,
            }

        except Exception as error:
            st.error(
                "Could not evaluate the translation. "
                "Check your API configuration and try again."
            )
            st.caption(f"Error: {type(error).__name__}: {error}")

    feedback = st.session_state.translation_feedback
    request = st.session_state.translation_last_request

    if feedback and request:
        st.divider()
        st.subheader("Translation Feedback")

        st.metric(
            "Translation score",
            f"{feedback['score']} / 5",
        )

        st.markdown("**Reference translation (English)**")
        st.write(feedback["reference_translation"])

        st.markdown("**Meaning**")
        st.write(feedback["meaning_feedback"])

        st.markdown("**Grammar**")
        st.write(feedback["grammar_feedback"])

        st.markdown("**Natural phrasing**")
        st.write(feedback["naturalness_feedback"])

        st.markdown("**Suggested improvement**")
        st.write(feedback["improved_translation"])

        st.info(feedback["overall_feedback"])

        with st.expander("Review your original attempt"):
            st.markdown(f"**Original ({request['source_language']})**")
            st.write(request["source_text"])

            st.markdown("**Your English translation**")
            st.write(request["learner_translation"])

        st.button(
            "Try Another Translation",
            on_click=_request_new_exercise,
        )