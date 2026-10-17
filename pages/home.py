
import streamlit as st


def app():
    st.title("📘 Language Tutor AI")

    st.write(
        "Welcome to your personal AI-powered language-learning assistant!"
    )

    st.markdown(
        """
        Improve your language skills through interactive exercises,
        AI-generated questions, reading activities, translation feedback,
        speaking practice, and image-based comprehension.
        """
    )

    st.divider()
    st.subheader("Your Learning Activities")

    with st.container(border=True):
        st.markdown("### 📘 Grammar Practice")
        st.write(
            "Strengthen your grammar through multiple-choice questions on "
            "tenses, articles, prepositions, subject-verb agreement, and more."
        )

    with st.container(border=True):
        st.markdown("### 📚 Vocabulary Practice")
        st.write(
            "Learn useful words by topic, test your understanding, and review "
            "definitions, example sentences, and explanations."
        )

    with st.container(border=True):
        st.markdown("### 📖 Reading Comprehension")
        st.write(
            "Read a level-appropriate passage, answer comprehension questions, "
            "and review explanations after submitting your answers."
        )

    with st.container(border=True):
        st.markdown("### 🌐 Translation Practice")
        st.write(
            "Translate sentences between supported languages and receive "
            "feedback on meaning, grammar, and natural phrasing."
        )

    with st.container(border=True):
        st.markdown("### 🎙️ Speaking Practice")
        st.write(
            "Read an AI-generated paragraph aloud in Telugu, Hindi, or English. "
            "Record your reading and receive transcription and improvement feedback."
        )

    with st.container(border=True):
        st.markdown("### 🖼️ Image Comprehension")
        st.write(
            "Describe an image aloud in Telugu, Hindi, or English. "
            "Receive feedback on your description, relevant details, "
            "grammar, and vocabulary."
        )

    st.divider()

    st.info(
        "Choose a learning activity from the sidebar to begin. "
        "Speaking Practice and Image Comprehension use browser-based "
        "audio recording."
    )
