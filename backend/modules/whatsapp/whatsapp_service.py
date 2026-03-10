import os
import json
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
TEMPLATE_NAME = os.getenv("WHATSAPP_TEMPLATE_NAME")  # kept for backward compatibility
API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"


def send_whatsapp_message(to_number: str, template_name: str, components: list):
    """
    Generic WhatsApp template sender used by all template functions.
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
            "name": template_name,
            "language": {"code": "en"},
            "components": components
        }
    }

    print("📤 Sending WhatsApp payload:")
    print(json.dumps(payload, indent=2))

    response = None

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ WhatsApp API error: {e}")

        if response and response.text:
            print("Response text:", response.text)

        return {
            "error": str(e),
            "details": response.text if response else None
        }


def send_whatsapp_template(to_number: str, patient_name: str, dynamic_url: str):
    """
    Send the original WhatsApp template.

    Body parameter:
    {{1}} -> patient_name

    Button parameter:
    {{1}} -> dynamic_url
    """

    components = [
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

    return send_whatsapp_message(
        to_number,
        TEMPLATE_NAME,
        components
    )


def send_whatsapp_new_template(to_number: str, patient_name: str, lab_name: str, signed_url: str):
    """
    Send the approved template "report_ready_notification_2".

    Body parameters:
    {{1}} -> patient_name
    {{2}} -> lab_name

    Button parameter:
    {{1}} -> signed_url
    """

    components = [
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

    return send_whatsapp_message(
        to_number,
        "report_ready_notification_2",
        components
    )