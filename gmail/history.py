def history_and_msg_id(service, history_id):
    query = service.users().history().list(
        userId="me",
        startHistoryId=history_id,
        historyTypes=["messageAdded"]
    ).execute()

    history = query.get('history', [])
    new_history_id = query.get('historyId', history_id)

    msg_ids = set()

    for i in history:
        messages = i.get('messagesAdded', [])
        for m in messages:
            msg_ids.add(m['message']['id'])
    
    return list(msg_ids), new_history_id