import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

def generate_response(prompt, chat_history):

    messages = [
        {
            "role": "system",
            "content": """
You are a medical report assistant chatbot.

Rules:
- Answer in 2-3 short lines
- Use simple patient-friendly language
- Avoid complex medical terms
- Be clear and concise
"""
        }
    ]

    messages.extend(chat_history)

    messages.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "model": "mistral:7b-instruct-v0.2-q2_K",
        "messages": messages,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    reply = response.json()['message']['content']

    # 🧠 Save memory
    chat_history.append({"role": "user", "content": prompt})
    chat_history.append({"role": "assistant", "content": reply})

    return reply
