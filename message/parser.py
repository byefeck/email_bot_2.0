import re
import logging
from message.cleaner import decode, decode_html

def extract_text_parts(parts):
    text_plain = None
    text_html = None

    for part in parts:
        mime = part.get("mimeType")
        data = part.get("body", {}).get("data")

        if "parts" in part:
            p, h = extract_text_parts(part["parts"])
            text_plain = text_plain or p
            text_html = text_html or h
            continue

        if not data:
            continue

        if mime == "text/plain":
            text_plain = decode(data)

        elif mime == "text/html":
            text_html = decode_html(data)

    return text_plain, text_html

def has_attachments(msg):
    payload = msg["payload"]

    if "parts" not in payload:
        return False

    for part in payload["parts"]:
        if part.get("filename"):  # если имя файла есть
            return True

    return False

def parse_sender(sender):
    email = re.search(r"<(.+?)>", sender)
    email = email.group(1) if email else ""
    name = re.sub(r"<.+?>", "", sender).replace('"', "").strip()
    return name, email

def parse_recipients(recipients_raw):
    # Header can contain multiple recipients separated by commas.
    # We extract all valid emails and normalize them for comparison.
    found_emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", recipients_raw or "")
    return [email.strip().lower() for email in found_emails]

def get_text(msg):
    payload = msg['payload']

    if 'parts' in payload:
        plain, html = extract_text_parts(payload['parts'])

        if plain:
            return plain
        if html:
            return html

    data = payload.get('body', {}).get('data')
    if data:
        return decode(data)

    return ""
        
def safe_get_message(service, msg_id):
    try:
        return service.users().messages().get(
            userId="me",
            id=msg_id
        ).execute()
    except Exception as e:
        logging.error(f"Message {msg_id} not found (skipped): {e}")
        return None

def parse_message(service, msg_id):
    msg = safe_get_message(service, msg_id)

    if not msg:
        return None

    headers = msg["payload"]["headers"]

    subject = next((i['value'] for i in headers if i['name'] == 'Subject'), 'Без темы')
    sender = next((i['value'] for i in headers if i['name'] == 'From'), 'Неизвестно')
    recipients_raw = next((i['value'] for i in headers if i['name'] == 'To'), '')
    name, email = parse_sender(sender)
    recipient_emails = parse_recipients(recipients_raw)
    text = get_text(msg)
    has_att = has_attachments(msg)

    return {
        'sender_name': name,
        'sender_email': email.strip().lower(),
        'recipient_emails': recipient_emails,
        'subject': subject,
        'text': text,
        'has_att': has_att
    }