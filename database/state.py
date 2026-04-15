import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATE_FILE = os.path.join(BASE_DIR, 'json', 'state.json')

def load_state():
    if not os.path.exists(STATE_FILE):
        save_state({})
        return {}
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w", encoding='utf-8') as f:
        json.dump(state, f, indent=2)
