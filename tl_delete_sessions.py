import os, sys, time, telethon, telethon.sync, utility as utl


for index, arg in enumerate(sys.argv):
    if index == 1:
        mbots_uniq_id = arg
    elif index == 2:
        from_id = int(arg)
    elif index == 3:
        type_ = arg

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())

cs = utl.Database()
cs = cs.data()

cs.execute(f"SELECT * FROM {utl.admin}")
row_admin = cs.fetchone()

cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{mbots_uniq_id}'")
row_mbots = cs.fetchone()

try:
    client = telethon.sync.TelegramClient(session=f"{directory}/sessions/{row_mbots['uniq_id']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
    client.connect()
    if type_ == 'all':
        if client.is_user_authorized():
            for session in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
                if not session.current:
                    try:
                        client(telethon.functions.account.ResetAuthorizationRequest(hash=session.hash))
                    except:
                        pass
        else:
            cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
    elif type_ == 'one':
        if client.is_user_authorized():
            is_ok = True
            count_other_sessions = 0
            for session in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
                if not session.current:
                    try:
                        count_other_sessions += 1
                        client(telethon.functions.account.ResetAuthorizationRequest(hash=session.hash))
                    except:
                        is_ok = False
                        break
            if not is_ok:
                utl.bot.send_message(
                    chat_id=from_id,
                    text="❌ An issue occurred while ending the remaining sessions\n\n"
                         "If you registered the account less than 24 hours ago, try again after 24 hours"
                )
            elif count_other_sessions == 0:
                utl.bot.send_message(chat_id=from_id, text="✅ There are no other sessions")
            else:
                utl.bot.send_message(chat_id=from_id, text="✅ The remaining sessions have been successfully logged out")
        else:
            cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
            utl.bot.send_message(chat_id=from_id, text="❌ The account has been disabled")
except Exception as e:
    print(e)
