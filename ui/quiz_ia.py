import streamlit as st

QUESTIONS = [
    {
        "question": f"Question {i+1}: choisissez la bonne réponse.",
        "options": ["Option A", "Option B", "Option C"],
        "answer": "Option A",
    }
    for i in range(30)
]

def run_quiz():
    st.header("🎯 QCM de validation")
    answers = []
    for idx, q in enumerate(QUESTIONS):
        answers.append(
            st.radio(q["question"], q["options"], key=f"q{idx}")
        )
    if st.button("Valider le QCM"):
        score = sum(a == q["answer"] for a, q in zip(answers, QUESTIONS))
        st.session_state["quiz_score"] = score
        st.success(f"Score obtenu : {score}/30")
    return st.session_state.get("quiz_score")
