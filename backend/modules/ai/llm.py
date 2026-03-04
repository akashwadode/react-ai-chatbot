"""
modules/ai/llm.py

Handles communication with local Ollama LLM.
Responsible only for sending prompt and returning AI response.
"""

import requests
from modules.ai.prompts import SYSTEM_PROMPT  # import the centralized prompt

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

def generate_response(prompt: str, chat_history: list):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT   # use from prompts.py
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

    try:
        data = response.json()

        if "message" in data:
            reply = data["message"]["content"]
        elif "error" in data:
            return f"AI Error: {data['error']}"
        else:
            return "Unexpected AI response format."

    except Exception as e:
        print("OLLAMA ERROR:", e)
        return "AI response failed."

    # Save conversation memory
    chat_history.append({"role": "user", "content": prompt})
    chat_history.append({"role": "assistant", "content": reply})

    return reply