import os
import shutil
import sys
import time
import json
import telethon
import telethon.sync
import utility as utl


for index, arg in enumerate(sys.argv):
    if index == 1:
        mbots_uniq_id = arg
    elif index == 2:
        from_id = int(arg)
    elif index == 3:
        folder_name = arg

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())

cs = utl.Database()
cs = cs.data()

is_ok = False
cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{mbots_uniq_id}'")
row_mbots = cs.fetchone()
folder_name = row_mbots["uniq_id"]
data_file_name = f"{directory}/data/{row_mbots['phone']}.json"
print(data_file_name)
print("archive session started")
try:
    shutil.copyfile(f"{directory}/sessions/{row_mbots['uniq_id']}.session", f"{directory}/sessions/{row_mbots['phone']}.session")
    client = telethon.sync.TelegramClient(session=f"{directory}/sessions/{row_mbots['phone']}", api_id=row_mbots["api_id"], api_hash=row_mbots["api_hash"])
    client.connect()
    print("client connected")
    if client.is_user_authorized():
        is_ok_temp = False
        for session in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
            if session.current:
                is_ok_temp = True
                break
        print("is_ok_temp", is_ok_temp)
        get_me = client.get_me()
        print("get_me", get_me)
        password = row_mbots["password"] if row_mbots["password"] is not None and row_mbots["password"] != "" else None
        if is_ok_temp:
            info_session = {
                "session_file": row_mbots["uniq_id"],
                "phone": row_mbots["phone"],
                "register_time": int(session.date_created.timestamp()),
                "app_id": row_mbots["api_id"],
                "app_hash": row_mbots["api_hash"],
                "sdk": session.platform,
                "app_version": session.app_version,
                "device": session.device_model,
                "last_check_time": int(time.time()),
                "avatar": "null",
                "first_name": get_me.first_name,
                "last_name": get_me.last_name,
                "username": None,
                "sex": None,
                "lang_code": "en",
                "system_lang_code": "en-US",
                "proxy": None,
                "ipv6": False,
                "password_2fa": password,
            }
            if not os.path.exists(f"{directory}/data"):
                os.makedirs(f"{directory}/data")

            with open(data_file_name, "w") as file:
                json.dump(info_session, file)
    else:
        print("client not authorized")
        cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
except Exception as e:
    print(e)
