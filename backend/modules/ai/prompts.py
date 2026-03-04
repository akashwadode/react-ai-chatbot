"""
ai/prompts.py

Central location for all prompt templates used by the AI module.
This keeps prompts separate from the LLM calling logic.
"""

# System prompt: defines the assistant's personality and constraints
SYSTEM_PROMPT = (
    "You are a medical report assistant chatbot.\n"
    "Rules:\n"
    "- Answer in 2-3 short lines\n"
    "- Use simple patient-friendly language\n"
    "- Avoid complex medical terms\n"
    "- Be clear and concise"
)

def build_user_prompt(question: str, report_context: str) -> str:
    """
    Builds the user prompt for a general chat question.
    Includes the patient's report context and the user's question.
    """
    return f"""
Answer the following question based on the patient report.

Question: {question}

Patient Report:
{report_context}
"""