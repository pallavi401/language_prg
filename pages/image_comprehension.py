"""Image Comprehension: describe a random image aloud and receive feedback."""

import requests
import streamlit as st

from services.speech_service import (
    LANGUAGES,
    evaluate_image_description,
    validate_recording,
)


RANDOM_IMAGE_URL = "https://picsum.photos/1280/720"


def fetch_random_image():
    """Fetch a random image and return its bytes and MIME type."""
    response = requests.get(
        RANDOM_IMAGE_URL,
        params={"random": st.session_state["image_comprehension_image_id"]},
        timeout=20,
    )
    response.raise_for_status()

    image_mime_type = response.headers.get(
        "Content-Type", "image/jpeg"
    ).split(";")[0]

    if not image_mime_type.startswith("image/"):
        raise ValueError("The image service did not return a valid image.")

    return response.content, image_mime_type


def app():
    st.title("🖼️ Image Comprehension")

    st.write(
        "Improve your speaking skills by describing an image in "
        "Telugu, Hindi, or English. Receive feedback on relevance, "
        "grammar, vocabulary, and your overall description."
    )

    # Initialize session state
    if "image_comprehension_image_id" not in st.session_state:
        st.session_state["image_comprehension_image_id"] = 0

    if "image_comprehension_image_bytes" not in st.session_state:
        st.session_state["image_comprehension_image_bytes"] = None

    if "image_comprehension_mime_type" not in st.session_state:
        st.session_state["image_comprehension_mime_type"] = None

    if "image_comprehension_feedback" not in st.session_state:
        st.session_state["image_comprehension_feedback"] = None

    if "image_comprehension_recording_id" not in st.session_state:
        st.session_state["image_comprehension_recording_id"] = 0

    # Choose description language
    language = st.selectbox(
        "Choose the language for your description",
        options=list(LANGUAGES.keys()),
        key="image_language",
    )

    # Start with a random image
    if st.button("🎲 Start", type="primary"):
        try:
            with st.spinner("Fetching a random image..."):
                st.session_state["image_comprehension_image_id"] += 1

                image_bytes, image_mime_type = fetch_random_image()

                st.session_state["image_comprehension_image_bytes"] = (
                    image_bytes
                )
                st.session_state["image_comprehension_mime_type"] = (
                    image_mime_type
                )
                st.session_state["image_comprehension_feedback"] = None
                st.session_state["image_comprehension_recording_id"] += 1

        except Exception as exc:
            st.error(f"Could not fetch an image: {exc}")

    image_bytes = st.session_state["image_comprehension_image_bytes"]
    image_mime_type = st.session_state["image_comprehension_mime_type"]

    if image_bytes is not None:
        st.subheader("Look carefully at the image")

        st.image(
            image_bytes,
            caption="Describe this image",
            use_container_width=True,
        )

        st.write(
            "Describe the people, objects, setting, actions, and other "
            "details you notice. Keep your recording within 30 seconds."
        )

        # Use a unique widget key for every new image.
        recording = st.audio_input(
            "🎙️ Record your image description",
            key=(
                "image_description_recording_"
                f"{st.session_state['image_comprehension_recording_id']}"
            ),
        )

        if recording is not None:
            audio_bytes = recording.getvalue()

            st.audio(audio_bytes, format="audio/wav")

            try:
                duration = validate_recording(audio_bytes)
                st.caption(f"Recording duration: {duration:.1f} seconds")

                if st.button(
                    "Evaluate my description",
                    type="primary",
                    key="evaluate_image_description",
                ):
                    try:
                        with st.spinner(
                            "Transcribing your speech and analysing the image..."
                        ):
                            feedback = evaluate_image_description(
                                audio_bytes=audio_bytes,
                                image_bytes=image_bytes,
                                image_mime_type=image_mime_type,
                                language=language,
                            )

                        st.session_state[
                            "image_comprehension_feedback"
                        ] = feedback

                        st.session_state[
                            "image_comprehension_feedback_image_id"
                        ] = st.session_state[
                            "image_comprehension_image_id"
                        ]

                        st.session_state[
                            "image_comprehension_feedback_language"
                        ] = language

                    except Exception as exc:
                        st.error(
                            f"Could not evaluate your description: {exc}"
                        )

            except ValueError as exc:
                st.warning(str(exc))

        # Show feedback only for the current image and language.
        feedback = st.session_state.get(
            "image_comprehension_feedback"
        )

        feedback_matches_current_image = (
            st.session_state.get(
                "image_comprehension_feedback_image_id"
            )
            == st.session_state["image_comprehension_image_id"]
        )

        feedback_matches_current_language = (
            st.session_state.get(
                "image_comprehension_feedback_language"
            )
            == language
        )

        if (
            feedback
            and feedback_matches_current_image
            and feedback_matches_current_language
        ):
            st.divider()
            st.subheader("Your feedback")

            st.markdown("**Transcript**")
            st.write(
                feedback.get("transcript", "No transcript returned.")
            )

            st.markdown("**Relevant details you mentioned**")
            relevant_details = feedback.get("relevant_details", [])

            if relevant_details:
                for item in relevant_details:
                    st.write(f"- {item}")
            else:
                st.write("No relevant details were returned.")

            st.markdown("**Details you could also mention**")
            missed_details = feedback.get("missed_details", [])

            if missed_details:
                for item in missed_details:
                    st.write(f"- {item}")
            else:
                st.write("No additional details were reported.")

            unsupported_claims = feedback.get("unsupported_claims", [])

            if unsupported_claims:
                st.markdown(
                    "**Details that may not match the image**"
                )
                for item in unsupported_claims:
                    st.write(f"- {item}")

            st.markdown("**Grammar feedback**")
            st.write(feedback.get("grammar_feedback", ""))

            st.markdown("**Example improved description**")
            st.info(
                feedback.get("improved_description", "")
            )

            st.success(
                feedback.get("overall_feedback", "Keep practising!")
            )

            st.divider()

            # Move to another image
            if st.button(
                "➡️ Next Image",
                type="primary",
                key="next_comprehension_image",
            ):
                st.session_state["image_comprehension_image_id"] += 1
                st.session_state["image_comprehension_feedback"] = None
                st.session_state["image_comprehension_recording_id"] += 1

                try:
                    with st.spinner("Fetching the next image..."):
                        image_bytes, image_mime_type = fetch_random_image()

                        st.session_state[
                            "image_comprehension_image_bytes"
                        ] = image_bytes

                        st.session_state[
                            "image_comprehension_mime_type"
                        ] = image_mime_type

                    st.rerun()

                except Exception as exc:
                    st.error(f"Could not fetch the next image: {exc}")

    else:
        st.info("Click **Start** to display a random image and begin.")


if __name__ == "__main__":
    app()