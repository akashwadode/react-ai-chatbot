import os
import json  
import requests
from urllib.parse import urljoin
from core.database import get_connection

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
TEMPLATE_NAME = os.getenv("WHATSAPP_TEMPLATE_NAME")
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

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"WhatsApp API error: {e}")
        if response and response.text:
            print("Response text:", response.text)
        return {"error": str(e), "details": response.text if response else None}
    
def update_notification_status(notification_id: str, status_id: int, retry_count: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if retry_count is not None:
        cursor.execute("""
            UPDATE dev.patient_notification_details
            SET notification_status_id = %s,
                retry_count = %s,
                processed_at = NOW()
            WHERE notification_id = %s
        """, (status_id, retry_count, notification_id))
    else:
        cursor.execute("""
            UPDATE dev.patient_notification_details
            SET notification_status_id = %s,
                processed_at = NOW()
            WHERE notification_id = %s
        """, (status_id, notification_id))
    conn.commit()
    cursor.close()
    conn.close()

def send_whatsapp_template(to_number: str, patient_name: str, dynamic_url: str):
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

    # 🔍 LOG THE FULL PAYLOAD
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
    
    
def send_whatsapp_static_template(to_number: str, patient_name: str):
    """
    Send a template with a static URL (no button parameter).
    Uses the same TEMPLATE_NAME from .env (assumed to be the static one).
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
            "name": TEMPLATE_NAME,   # e.g., "health_report_ready_cta"
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": patient_name}
                    ]
                }
            ]
        }
    }

    print("📤 Sending static WhatsApp payload:")
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