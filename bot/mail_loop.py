import asyncio
import logging

from gmail.service import get_service
from gmail.history import history_and_msg_id
from message.parser import parse_message
from message.formater import format_msg
from database.state import load_state, save_state

PROCESSED_IDS_KEY = "processed_msg_ids"
MAX_PROCESSED_IDS = 1000

def _prepare_processed_ids(state):
    processed_ids = state.get(PROCESSED_IDS_KEY, [])
    if not isinstance(processed_ids, list):
        processed_ids = []
    return processed_ids

def _remember_processed_id(state, processed_ids, msg_id):
    processed_ids.append(msg_id)
    if len(processed_ids) > MAX_PROCESSED_IDS:
        processed_ids[:] = processed_ids[-MAX_PROCESSED_IDS:]
    state[PROCESSED_IDS_KEY] = processed_ids
    save_state(state)

async def mail_loop(bot, CHAT_ID, THREAD_ID):
    service = get_service()

    state = load_state()
    history_id = state.get('history_id')
    processed_ids = _prepare_processed_ids(state)
    processed_ids_set = set(processed_ids)

    if not history_id:
        profile = service.users().getProfile(userId='me').execute()
        history_id = profile['historyId']
        state["history_id"] = history_id
        save_state(state)

    while True:
        try:
            msg_ids, new_history_id = history_and_msg_id(service, history_id)
            for msg_id in msg_ids:
                try:
                    if msg_id in processed_ids_set:
                        continue
                    msg_dict = parse_message(service, msg_id)
                    if not msg_dict:
                        continue
                    sender_email = msg_dict.get("sender_email", "")
                    recipient_emails = msg_dict.get("recipient_emails", [])
                    if sender_email and sender_email in recipient_emails:
                        processed_ids_set.add(msg_id)
                        _remember_processed_id(state, processed_ids, msg_id)
                        continue
                    send = format_msg(msg_dict)
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=send,
                        message_thread_id=int(THREAD_ID) if THREAD_ID else None
                    )
                    processed_ids_set.add(msg_id)
                    _remember_processed_id(state, processed_ids, msg_id)
                    await asyncio.sleep(5)
                except Exception as e:
                    logging.error(f"Ошибка обработки msg {msg_id}: {e}")
                    continue
            history_id = new_history_id
            state['history_id'] = history_id
            save_state(state)
        except Exception as e:
            logging.error(f"Ошибка mail_loop: {e}")
        await asyncio.sleep(5)