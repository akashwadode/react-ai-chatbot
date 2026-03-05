import os
import requests
from urllib.parse import urljoin

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
TEMPLATE_NAME = os.getenv("WHATSAPP_TEMPLATE_NAME")
API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

def send_whatsapp_template(to_number: str, dynamic_url: str):
    """
    Send a template WhatsApp message with the dynamic URL as a parameter.
    """
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": dynamic_url}
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"WhatsApp API error: {e}")
        if response.text:
            print(response.text)
        return {"error": str(e)}