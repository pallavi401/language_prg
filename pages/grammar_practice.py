
import streamlit as st

from services.ai_service import generate_grammar_questions


TOPICS = [
    "Present Simple Tense",
    "Past Simple Tense",
    "Future Tense",
    "Articles",
    "Prepositions",
    "Subject-Verb Agreement",
    "Conditional Sentences",
]

LEVELS = ["Beginner", "Intermediate", "Advanced"]


def app():
    st.header("Grammar Practice")
    st.write(
        "Improve your English grammar with AI-generated "
        "multiple-choice questions."
    )

    # Initialize state once per Streamlit session.
    if "grammar_quiz" not in st.session_state:
        st.session_state.grammar_quiz = None

    if "grammar_submitted" not in st.session_state:
        st.session_state.grammar_submitted = False

    # Quiz configuration.
    topic = st.selectbox("Grammar topic", TOPICS)
    level = st.selectbox("Learner level", LEVELS)
    number_of_questions = st.selectbox(
        "Number of questions",
        [3, 5, 10],
        index=0,
    )

    # Generate a new quiz using the existing AI service.
    if st.button("Generate Quiz", type="primary"):
        try:
            with st.spinner("Generating your grammar quiz..."):
                quiz = generate_grammar_questions(
                    topic=topic,
                    level=level,
                    number_of_questions=number_of_questions,
                )

            # Remove previous answers before displaying the new quiz.
            old_quiz = st.session_state.grammar_quiz

            if old_quiz:
                for question in old_quiz["questions"]:
                    answer_key = f"grammar_answer_{question['id']}"
                    st.session_state.pop(answer_key, None)

            st.session_state.grammar_quiz = quiz
            st.session_state.grammar_submitted = False

        except Exception as error:
            st.error(
                "Could not generate the quiz. "
                "Please check your API configuration and try again."
            )
            st.caption(f"Error: {type(error).__name__}: {error}")

    quiz = st.session_state.grammar_quiz

    if not quiz:
        st.info("Choose your options and select Generate Quiz to begin.")
        return

    st.divider()
    st.subheader(f"Topic: {quiz['topic']}")
    st.caption(f"Level: {quiz['level']}")

    # Display questions without revealing their correct answers.
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
            key=f"grammar_answer_{question['id']}",
            index=None,
            disabled=st.session_state.grammar_submitted,
            label_visibility="collapsed",
        )

    if not st.session_state.grammar_submitted:
        if st.button("Submit Answers"):
            st.session_state.grammar_submitted = True
            st.rerun()

    # Evaluate and show feedback only after submission.
    if st.session_state.grammar_submitted:
        correct_count = 0
        unanswered_count = 0

        for question in quiz["questions"]:
            answer_key = f"grammar_answer_{question['id']}"
            selected_answer = st.session_state.get(answer_key)

            if selected_answer is None:
                unanswered_count += 1
            elif selected_answer == question["correct_answer"]:
                correct_count += 1

        total = len(quiz["questions"])

        st.divider()
        st.subheader("Your Results")
        st.metric("Score", f"{correct_count} / {total}")

        if unanswered_count:
            st.warning(
                f"You left {unanswered_count} question(s) unanswered."
            )

        for question in quiz["questions"]:
            answer_key = f"grammar_answer_{question['id']}"
            selected_answer = st.session_state.get(answer_key)
            correct_answer = question["correct_answer"]

            st.markdown(f"**Question {question['id']}**")

            if selected_answer == correct_answer:
                st.success("Correct!")
            else:
                st.error(
                    f"Incorrect. Correct answer: "
                    f"{correct_answer}. "
                    f"{question['options'][correct_answer]}"
                )

            st.write(f"Explanation: {question['explanation']}")

        if st.button("Start New Quiz"):
            st.session_state.grammar_quiz = None
            st.session_state.grammar_submitted = False

            for question in quiz["questions"]:
                answer_key = f"grammar_answer_{question['id']}"
                st.session_state.pop(answer_key, None)

            st.rerun()
