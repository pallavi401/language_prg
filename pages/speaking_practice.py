"""Speaking Practice: read a paragraph aloud and receive feedback."""

import streamlit as st

from services.speech_service import (
    LANGUAGES,
    LEVELS,
    evaluate_speaking,
    generate_reading_paragraph,
    validate_recording,
)


def app():
    st.title("🎙️ Speaking Practice")

    # Initialize session state
    if "speaking_paragraph" not in st.session_state:
        st.session_state["speaking_paragraph"] = None

    if "speaking_evaluation" not in st.session_state:
        st.session_state["speaking_evaluation"] = None

    if "speaking_recording_id" not in st.session_state:
        st.session_state["speaking_recording_id"] = 0

    st.write(
        "Read a paragraph aloud in Telugu, Hindi, or English. "
        "Record once and receive feedback."
    )

    # Select language and difficulty
    language = st.selectbox(
        "Choose your language",
        options=list(LANGUAGES.keys()),
        key="speaking_language",
    )

    level = st.selectbox(
        "Choose your difficulty",
        options=LEVELS,
        key="speaking_level",
    )

    # Generate a paragraph
    if st.button("Generate paragraph", type="primary"):
        try:
            with st.spinner("Generating a new paragraph..."):
                paragraph = generate_reading_paragraph(language, level)

            st.session_state["speaking_paragraph"] = paragraph
            st.session_state["speaking_paragraph_language"] = language
            st.session_state["speaking_evaluation"] = None
            st.session_state.pop("speaking_feedback", None)

            # Create a fresh recording widget
            st.session_state["speaking_recording_id"] += 1

        except Exception as exc:
            st.error(f"Could not generate the paragraph: {exc}")

    paragraph = st.session_state.get("speaking_paragraph")
    paragraph_language = st.session_state.get("speaking_paragraph_language")

    # Display paragraph and recording interface
    if paragraph and paragraph_language == language:
        st.subheader("Your paragraph")
        st.info(paragraph)

        st.caption(
            "Read the paragraph naturally. "
            "Keep your recording within 30 seconds."
        )

        # A unique key allows each practice attempt to use a fresh recording.
        recording = st.audio_input(
            "Record yourself reading the paragraph",
            key=(
                f"speaking_recording_"
                f"{st.session_state['speaking_recording_id']}"
            ),
        )

        if recording is not None:
            audio_bytes = recording.getvalue()

            st.audio(audio_bytes, format="audio/wav")

            try:
                duration = validate_recording(audio_bytes)
                st.caption(f"Recording duration: {duration:.1f} seconds")

                if st.button("Evaluate my reading", type="primary"):
                    try:
                        with st.spinner(
                            "Transcribing and evaluating your reading..."
                        ):
                            feedback = evaluate_speaking(
                                audio_bytes=audio_bytes,
                                language=language,
                                reference_paragraph=paragraph,
                            )

                        st.session_state["speaking_feedback"] = feedback
                        st.session_state["speaking_evaluation"] = True

                    except Exception as exc:
                        st.error(
                            f"Could not evaluate your recording: {exc}"
                        )

            except ValueError as exc:
                st.warning(str(exc))

        # Display feedback after evaluation
        feedback = st.session_state.get("speaking_feedback")

        if feedback:
            st.divider()
            st.subheader("Your feedback")

            st.markdown("**Transcript**")
            st.write(
                feedback.get("transcript", "No transcript returned.")
            )

            st.markdown("**Words or phrases read correctly**")
            observations = feedback.get("matching_observations", [])

            if observations:
                for item in observations:
                    st.write(f"- {item}")
            else:
                st.write("No matching observations were returned.")

            st.markdown("**Differences from the paragraph**")
            differences = feedback.get("differences", [])

            if differences:
                for item in differences:
                    st.write(f"- {item}")
            else:
                st.write("No differences were reported.")

            st.markdown("**Grammar feedback**")
            st.write(feedback.get("grammar_feedback", ""))

            st.markdown("**Tips for improvement**")
            tips = feedback.get("improvement_tips", [])

            if tips:
                for tip in tips:
                    st.write(f"- {tip}")
            else:
                st.write("No improvement tips were returned.")

            st.success(
                feedback.get("overall_feedback", "Keep practising!")
            )

            # Generate another paragraph after completing evaluation
            st.divider()

            if st.button(
                "🔄 Generate New Paragraph",
                key="generate_new_speaking_paragraph",
                type="primary",
            ):
                st.session_state["speaking_paragraph"] = None
                st.session_state["speaking_evaluation"] = None

                st.session_state.pop(
                    "speaking_paragraph_language", None
                )
                st.session_state.pop("speaking_feedback", None)

                # Increment the key instead of modifying widget state.
                st.session_state["speaking_recording_id"] += 1

                st.rerun()

    elif paragraph and paragraph_language != language:
        st.info(
            "Click **Generate paragraph** to create one "
            "in the selected language."
        )


if __name__ == "__main__":
    app()