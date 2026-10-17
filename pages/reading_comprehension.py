import streamlit as st

from services.ai_service import generate_reading_comprehension

TOPICS = [
    "Daily Life", "Education", "Nature and Environment",
    "Science and Technology", "Health and Fitness",
    "Travel and Culture", "Work and Careers",
]
LEVELS = ["Beginner", "Intermediate", "Advanced"]


def _clear_answers(activity):
    if activity:
        for question in activity["questions"]:
            st.session_state.pop(f"reading_practice_answer_{question['id']}", None)


def app():
    st.header("Reading Comprehension")
    st.write("Read a passage, answer questions, and learn from the explanations.")

    if "reading_practice_activity" not in st.session_state:
        st.session_state.reading_practice_activity = None
    if "reading_practice_submitted" not in st.session_state:
        st.session_state.reading_practice_submitted = False

    topic = st.selectbox("Passage topic", TOPICS, key="reading_practice_topic")
    level = st.selectbox("Reading level", LEVELS, key="reading_practice_level")
    count = st.selectbox("Number of questions", [3, 5, 10], key="reading_practice_count")

    if st.button("Generate Reading Practice", type="primary"):
        try:
            with st.spinner("Creating your passage and questions..."):
                activity = generate_reading_comprehension(topic, level, count)
            _clear_answers(st.session_state.reading_practice_activity)
            st.session_state.reading_practice_activity = activity
            st.session_state.reading_practice_submitted = False
            st.rerun()
        except Exception as error:
            st.error("Could not generate reading practice. Check your API configuration.")
            st.caption(f"Error: {type(error).__name__}: {error}")

    activity = st.session_state.reading_practice_activity
    if not activity:
        st.info("Choose a topic and level, then generate a reading activity.")
        return

    st.divider()
    st.subheader(activity["title"])
    st.caption(f"Topic: {activity['topic']} · Level: {activity['level']}")
    st.markdown(activity["passage"])
    st.divider()
    st.subheader("Comprehension Questions")

    for question in activity["questions"]:
        st.markdown(f"**{question['id']}. {question['question']}**")
        st.radio(
            "Select an answer",
            ["A", "B", "C", "D"],
            format_func=lambda label, opts=question["options"]: f"{label}. {opts[label]}",
            key=f"reading_practice_answer_{question['id']}",
            index=None,
            disabled=st.session_state.reading_practice_submitted,
            label_visibility="collapsed",
        )

    if not st.session_state.reading_practice_submitted:
        if st.button("Submit Answers", type="primary"):
            st.session_state.reading_practice_submitted = True
            st.rerun()

    if st.session_state.reading_practice_submitted:
        correct = sum(
            st.session_state.get(f"reading_practice_answer_{q['id']}") == q["correct_answer"]
            for q in activity["questions"]
        )
        total = len(activity["questions"])
        st.divider()
        st.subheader("Your Results")
        st.metric("Score", f"{correct} / {total}")
        st.progress(correct / total if total else 0)

        for question in activity["questions"]:
            selected = st.session_state.get(f"reading_practice_answer_{question['id']}")
            answer = question["correct_answer"]
            st.markdown(f"**Question {question['id']}**")
            if selected == answer:
                st.success("Correct!")
            else:
                st.error(f"Correct answer: {answer}. {question['options'][answer]}")
            st.write(f"Explanation: {question['explanation']}")

        if st.button("Start New Practice"):
            _clear_answers(activity)
            st.session_state.reading_practice_activity = None
            st.session_state.reading_practice_submitted = False
            st.rerun()
