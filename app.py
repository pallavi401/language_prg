
import streamlit as st

from pages import (
    home,
    grammar_practice,
    vocabulary_practice,
    reading_comprehension,
    translation_practice,
    speaking_practice,
    image_comprehension,
)


st.set_page_config(
    page_title="Language Tutor AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGES = {
    "Home": home,
    "Grammar Practice": grammar_practice,
    "Vocabulary Practice": vocabulary_practice,
    "Reading Comprehension": reading_comprehension,
    "Translation Practice": translation_practice,
    "Speaking Practice": speaking_practice,
    "Image Comprehension": image_comprehension,
}


def main():
    st.sidebar.title("📘 Language Tutor AI")
    st.sidebar.caption("Your personal AI language-learning assistant")

    selection = st.sidebar.radio(
        "Choose a learning activity",
        options=list(PAGES.keys()),
    )

    page = PAGES[selection]
    page.app()


if __name__ == "__main__":
    main()
