import os
import json
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
TEMPLATE_NAME = os.getenv("WHATSAPP_TEMPLATE_NAME")  # kept for backward compatibility
API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"


def send_whatsapp_template(to_number: str, patient_name: str, dynamic_url: str):
    """
    Send a template WhatsApp message with:
    - Body parameter: patient_name (replaces {{1}})
    - URL button: dynamic_url (the signed report link)
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
                        {"type": "text", "text": patient_name}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": dynamic_url}
                    ]
                }
            ]
        }
    }

    print("📤 Sending WhatsApp payload:")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ WhatsApp API error: {e}")
        if response and response.text:
            print("Response text:", response.text)
        return {"error": str(e), "details": response.text if response else None}


def send_whatsapp_new_template(to_number: str, patient_name: str, lab_name: str, signed_url: str):
    """
    Send the new approved template "report_ready_notification_2".
    - Body expects two parameters: patient_name ({{1}}) and lab_name ({{2}})
    - Button expects one parameter: the full signed URL (for {{1}} in button)
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
            "name": "report_ready_notification_2",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": patient_name},
                        {"type": "text", "text": lab_name}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {"type": "text", "text": signed_url}
                    ]
                }
            ]
        }
    }

    print("📤 Sending new template payload:")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ WhatsApp API error: {e}")
        if response and response.text:
            print("Response text:", response.text)
        return {"error": str(e), "details": response.text if response else None}