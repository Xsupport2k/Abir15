import os, sys, time, telethon.sync, utility as utl


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
            if row_mbots['password'] is not None:
                try:
                    client.edit_2fa(current_password=row_mbots['password'])
                except:
                    pass
            cs.execute(f"UPDATE {utl.mbots} SET last_del_pass_at={timestamp} WHERE id={row_mbots['id']}")
        else:
            cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
    elif type_ == 'one':
        if client.is_user_authorized():
            if row_mbots['password'] is not None:
                try:
                    client.edit_2fa(current_password=row_mbots['password'])
                    utl.bot.send_message(chat_id=from_id, text="✅ The password has been successfully removed.")
                except:
                    utl.bot.send_message(chat_id=from_id, text="❌ The account password is different from the one stored in the database.")
            else:
                utl.bot.send_message(chat_id=from_id, text="❌ No password is stored in the database for the account")
            cs.execute(f"UPDATE {utl.mbots} SET last_del_pass_at={timestamp} WHERE id={row_mbots['id']}")
        else:
            cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
            utl.bot.send_message(chat_id=from_id, text="❌ The account has been disabled")
except Exception as e:
    print(e)
    