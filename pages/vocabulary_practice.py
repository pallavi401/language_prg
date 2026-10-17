
import streamlit as st

from services.ai_service import generate_vocabulary_questions


TOPICS = [
    "Daily Life",
    "Education",
    "Work and Careers",
    "Travel and Tourism",
    "Technology",
    "Health and Fitness",
    "Environment",
    "Emotions and Personality",
]

LEVELS = ["Beginner", "Intermediate", "Advanced"]


def _clear_previous_answers(quiz):
    """Remove stored answers associated with the supplied quiz."""

    if not quiz:
        return

    for question in quiz["questions"]:
        answer_key = f"vocabulary_answer_{question['id']}"
        st.session_state.pop(answer_key, None)


def app():
    st.header("Vocabulary Practice")

    st.write(
        "Build your English vocabulary by learning word meanings, "
        "choosing the correct answers, and reviewing example sentences."
    )

    # Initialize this page's session state once.
    if "vocabulary_quiz" not in st.session_state:
        st.session_state.vocabulary_quiz = None

    if "vocabulary_submitted" not in st.session_state:
        st.session_state.vocabulary_submitted = False

    # Quiz configuration.
    topic = st.selectbox(
        "Vocabulary topic",
        TOPICS,
        key="vocabulary_topic",
    )

    level = st.selectbox(
        "Learner level",
        LEVELS,
        key="vocabulary_level",
    )

    number_of_questions = st.selectbox(
        "Number of questions",
        [3, 5, 10],
        index=0,
        key="vocabulary_number_of_questions",
    )

    # Generate a new quiz.
    if st.button("Generate Vocabulary Quiz", type="primary"):
        try:
            with st.spinner("Generating your vocabulary quiz..."):
                quiz = generate_vocabulary_questions(
                    topic=topic,
                    level=level,
                    number_of_questions=number_of_questions,
                )

            # Remove answer state belonging to the previous quiz.
            _clear_previous_answers(
                st.session_state.vocabulary_quiz
            )

            st.session_state.vocabulary_quiz = quiz
            st.session_state.vocabulary_submitted = False

        except Exception as error:
            st.error(
                "Could not generate the vocabulary quiz. "
                "Please check your API configuration and try again."
            )
            st.caption(
                f"Error: {type(error).__name__}: {error}"
            )

    quiz = st.session_state.vocabulary_quiz

    if not quiz:
        st.info(
            "Choose a topic and level, then select "
            "Generate Vocabulary Quiz to begin."
        )
        return

    st.divider()
    st.subheader(f"Topic: {quiz['topic']}")
    st.caption(f"Learner level: {quiz['level']}")

    # Display questions without revealing their answers.
    for question in quiz["questions"]:
        st.markdown(
            f"**Question {question['id']}. "
            f"{question['question']}**"
        )

        option_labels = ["A", "B", "C", "D"]

        st.radio(
            "Choose your answer:",
            options=option_labels,
            format_func=lambda label, options=question["options"]: (
                f"{label}. {options[label]}"
            ),
            key=f"vocabulary_answer_{question['id']}",
            index=None,
            disabled=st.session_state.vocabulary_submitted,
            label_visibility="collapsed",
        )

    # Submit answers once.
    if not st.session_state.vocabulary_submitted:
        if st.button("Submit Answers"):
            st.session_state.vocabulary_submitted = True
            st.rerun()

    # Evaluate and reveal feedback after submission.
    if st.session_state.vocabulary_submitted:
        correct_count = 0
        unanswered_count = 0

        for question in quiz["questions"]:
            answer_key = f"vocabulary_answer_{question['id']}"
            selected_answer = st.session_state.get(answer_key)

            if selected_answer is None:
                unanswered_count += 1
            elif selected_answer == question["correct_answer"]:
                correct_count += 1

        total = len(quiz["questions"])

        st.divider()
        st.subheader("Your Results")

        st.metric(
            "Score",
            f"{correct_count} / {total}",
        )

        st.progress(correct_count / total if total else 0)

        if unanswered_count:
            st.warning(
                f"You left {unanswered_count} question(s) unanswered."
            )

        # Show feedback, definitions, and example sentences.
        for question in quiz["questions"]:
            answer_key = f"vocabulary_answer_{question['id']}"
            selected_answer = st.session_state.get(answer_key)
            correct_answer = question["correct_answer"]

            st.markdown(
                f"### Question {question['id']}: "
                f"{question['word']}"
            )

            if selected_answer == correct_answer:
                st.success("Correct!")
            else:
                st.error(
                    f"Incorrect. Correct answer: {correct_answer}. "
                    f"{question['options'][correct_answer]}"
                )

            st.markdown(
                f"**Meaning:** {question['definition']}"
            )

            st.markdown(
                f"**Example:** {question['example_sentence']}"
            )

            st.markdown(
                f"**Explanation:** {question['explanation']}"
            )

            st.divider()

        if st.button("Start New Quiz"):
            _clear_previous_answers(quiz)

            st.session_state.vocabulary_quiz = None
            st.session_state.vocabulary_submitted = False

            st.rerun()
