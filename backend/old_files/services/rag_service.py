from ..rag_pipeline import run_rag


def ask_patient_question(question: str, patient_id: int):

    try:
        result = run_rag(question, patient_id)

        return result.get(
            "answer",
            "Sorry, I couldn't understand that question related to your report."
        )

    except Exception as e:
        return str(e)
