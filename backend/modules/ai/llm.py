"""
modules/ai/llm.py

Handles communication with local Ollama LLM using the /api/chat endpoint.
Uses the mistral:7b-instruct model which understands the messages format.
"""

import requests
from modules.ai.prompts import SYSTEM_PROMPT

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "mistral:7b-instruct-v0.2-q2_K"   # <-- changed here

def generate_response(user_prompt: str, chat_history: list) -> str:
    """
    Sends a conversation to Ollama's chat endpoint.
    The messages array includes a system prompt, chat history, and the new user message.
    """
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Add the conversation history (already in OpenAI format)
    messages.extend(chat_history)

    # Add the new user message
    messages.append({
        "role": "user",
        "content": user_prompt
    })

    payload = {
        "model": "mistral:7b-instruct-v0.2-q2_K",
        "messages": messages,
        "stream": False,
        "options": {
            "max_tokens": 60,      # keep answers short
            "temperature": 0.3      # more deterministic
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if "message" in data:
            reply = data["message"]["content"].strip()
        elif "error" in data:
            reply = f"AI Error: {data['error']}"
        else:
            reply = "Unexpected AI response format."

    except Exception as e:
        print("OLLAMA ERROR:", e)
        reply = "AI response failed."

    # Update chat history with the new exchange
    chat_history.append({"role": "user", "content": user_prompt})
    chat_history.append({"role": "assistant", "content": reply})

    return reply