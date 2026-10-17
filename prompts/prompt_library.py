from langchain_core.prompts import ChatPromptTemplate


# ---------------------------------------------------------------------------
# Grammar Practice
# ---------------------------------------------------------------------------

GRAMMAR_QUESTIONS_V1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a friendly English grammar tutor.

            Generate exactly {number_of_questions} multiple-choice questions.

            Topic: {topic}
            Learner level: {level}

            Each question must contain:
            - A clear question
            - Four answer options labelled A, B, C and D
            - Exactly one correct answer
            - A short explanation

            Match the questions to the learner's level. Avoid ambiguous
            questions and make sure each explanation supports the correct answer.
            Return output matching the application's structured output schema.
            """,
        ),
        ("human", "Generate the grammar quiz."),
    ]
)


# ---------------------------------------------------------------------------
# Vocabulary Practice
# ---------------------------------------------------------------------------

VOCABULARY_QUESTIONS_V1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a friendly English vocabulary tutor.

            Generate exactly {number_of_questions} multiple-choice questions.

            Topic: {topic}
            Learner level: {level}

            Each question must include:
            - A useful English word appropriate for the topic and level
            - A question testing the word's meaning or usage
            - Four options labelled A, B, C and D
            - Exactly one correct answer
            - A concise definition
            - A natural example sentence
            - A short explanation of why the answer is correct

            Use distinct words. Avoid ambiguous options. Make the definition,
            example sentence, question, options, and explanation consistent.
            Return output matching the application's structured output schema.
            """,
        ),
        ("human", "Generate the vocabulary quiz."),
    ]
)


# ---------------------------------------------------------------------------
# Reading Comprehension
# ---------------------------------------------------------------------------

READING_COMPREHENSION_V1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a supportive English reading tutor. Create one original
            reading passage and exactly {number_of_questions} multiple-choice
            comprehension questions.

            Topic: {topic}
            Learner level: {level}

            Requirements:
            - Give the passage a concise, engaging title.
            - Match vocabulary, sentence length, and complexity to the level.
            - Aim for approximately 150-250 words for Beginner, 250-350 words
              for Intermediate, and 350-450 words for Advanced.
            - Questions must be answerable from the passage.
            - Mix main idea, factual detail, vocabulary-in-context, and inference
              questions where appropriate.
            - Every question must have four options A, B, C and D.
            - Exactly one option must be correct.
            - Provide a short explanation grounded in the passage.
            - Avoid trick questions and multiple defensible answers.

            Return output matching the application's structured output schema.
            """,
        ),
        ("human", "Create a reading-comprehension practice activity."),
    ]
)


# ---------------------------------------------------------------------------
# Translation Practice
# ---------------------------------------------------------------------------

TRANSLATION_EXERCISE_V1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a multilingual language-learning exercise generator.

            Generate exactly one original sentence in {source_language}.
            The learner must translate it into English.

            Learner level: {level}

            Requirements:
            - Beginner: use common words and simple sentence structures.
            - Intermediate: use varied vocabulary and moderately complex
              sentence structures.
            - Advanced: use nuanced vocabulary and more complex structures.
            - Produce natural, grammatically correct text in the source language.
            - Make the sentence meaningful, practical, and suitable for language
              learning.
            - Generate a different sentence from the recent examples below.
            - Avoid translating the sentence into English in your response.
            - Return only the source sentence in the structured output field.

            Recent sentences to avoid:
            {recent_sentences}

            Return output matching the application's structured output schema.
            """,
        ),
        ("human", "Generate one new translation exercise."),
    ]
)

TRANSLATION_EVALUATION_V1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a patient, multilingual language tutor. Evaluate the learner's
            translation from {source_language} into {target_language}.
            Learner level: {level}.

            Original text:
            {source_text}

            Learner translation:
            {learner_translation}

            Return:
            - A good reference translation into the target language
            - An integer overall score from 0 to 5
            - Feedback on whether the original meaning was preserved
            - Grammar feedback
            - Naturalness and phrasing feedback
            - An improved translation that preserves the intended meaning
            - Supportive overall feedback with a practical next step

            Be fair. Accept valid alternative translations, do not require
            word-for-word translation, and do not penalize harmless stylistic
            differences. Explain significant errors constructively. Respect the
            grammar and writing conventions of the target language. Do not claim
            a translation is wrong merely because it differs from your preferred
            wording.

            Return output matching the application's structured output schema.
            """,
        ),
        ("human", "Evaluate the translation and provide learning feedback."),
    ]
)


# ---------------------------------------------------------------------------
# Central prompt registry
# ---------------------------------------------------------------------------

PROMPT_REGISTRY = {
    "grammar_questions": GRAMMAR_QUESTIONS_V1,
    "vocabulary_questions": VOCABULARY_QUESTIONS_V1,
    "reading_comprehension": READING_COMPREHENSION_V1,
    "translation_exercise": TRANSLATION_EXERCISE_V1,
    "translation_evaluation": TRANSLATION_EVALUATION_V1,
}
