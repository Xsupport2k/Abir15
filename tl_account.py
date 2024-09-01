import shutil
import os, sys, time, telethon, telethon.sync, utility as utl

from config import sessions_channel


for index, arg in enumerate(sys.argv):
    if index == 1:
        mbots_uniq_id = arg
    elif index == 2:
        message_id = int(arg)
    elif index == 3:
        type_ = arg

directory = os.path.dirname(os.path.abspath(__file__))
timestamp = int(time.time())

cs = utl.Database()
cs = cs.data()

cs.execute(f"SELECT * FROM {utl.countries} WHERE id=1")
row_countries = cs.fetchone()

area_code = row_countries['area_code']

cs.execute(f"SELECT * FROM {utl.admin}")
row_admin = cs.fetchone()

cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{mbots_uniq_id}'")
row_mbots = cs.fetchone()
try:
    client = telethon.sync.TelegramClient(session=f"{directory}/sessions/{row_mbots['uniq_id']}", api_id=row_mbots["api_id"], api_hash=row_mbots["api_hash"])
    client.connect()
    if type_ == "code":
        me = client.send_code_request(phone=row_mbots["phone"])
        cs.execute(f"UPDATE {utl.mbots} SET phone_code_hash='{me.phone_code_hash}' WHERE id={row_mbots['id']}")
        cs.execute(f"UPDATE {utl.users} SET step='add_acc;code;{row_mbots['id']}' WHERE user_id={row_mbots['creator_user_id']}")
        utl.bot.send_message(
            chat_id=row_mbots["creator_user_id"], text="Enter the code on the first line and the password on the second line:\n\n" "Example:\n" "12345\n" "password\n\n" "⚠️ If the account does not have a password, just enter the code"
        )
    elif type_ == "auth":
        is_ok = True
        try:
            me = client.sign_in(phone=row_mbots["phone"], phone_code_hash=row_mbots["phone_code_hash"], code=row_mbots["code"])
        except telethon.errors.PhoneCodeInvalidError as e:
            utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ The code is incorrect")
            is_ok = False
        except telethon.errors.SessionPasswordNeededError as e:
            if row_mbots["password"] is None:
                utl.bot.send_message(
                    chat_id=row_mbots["creator_user_id"],
                text="❌ The account has a password!\n\n" "⚠️ Enter the code on the first line and the password on the second line",
                )
                is_ok = False
            else:
                me = client.sign_in(password=row_mbots["password"])
        if is_ok:
            cs.execute(f"UPDATE {utl.mbots} SET user_id={int(me.id)},status=3,last_check_exit_at={timestamp} WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={row_mbots['creator_user_id']}")
            utl.bot.send_message(
                chat_id=row_mbots["creator_user_id"],
                text=f"🔐 The account {row_mbots['phone']} was successfully retrieved\n\n"
                f"👈 To check the balance, please log out of the account and click the Final Registration button after {row_admin['time_logout_account']} seconds",
                    reply_markup={"inline_keyboard": [[{"text": "Final Registration", "callback_data": f"confirm_phone;{row_mbots['id']}"}]]},
            )
    elif type_ == "session":
        is_ok = True
        for session in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
            if not session.current:
                try:
                    client(telethon.functions.account.ResetAuthorizationRequest(hash=session.hash))
                except:
                    is_ok = False
        if is_ok:
            for session in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
                if not session.current:
                    is_ok = False
        if not is_ok:
            utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ You haven't logged out yet!", reply_to_message_id=message_id)
        else:
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={row_mbots['id']}")
            row_mbots = cs.fetchone()
            if row_mbots["status"] != 3:
                try:
                    utl.bot.delete_message(chat_id=row_mbots["creator_user_id"], message_id=message_id)
                except:
                    pass
                exit()
            cs.execute(f"UPDATE {utl.mbots} SET status=1 WHERE id={row_mbots['id']}")
            cs.execute(f"UPDATE {utl.users} SET balance=balance+{row_mbots['amount']} WHERE user_id={row_mbots['creator_user_id']}")
            utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text=f"✅ The account {row_mbots['phone']} has been registered, and {row_mbots['amount']} Tomans have been added to your balance")
            try:
                utl.bot.delete_message(chat_id=row_mbots["creator_user_id"], message_id=message_id)
            except:
                pass
            utl.bot.send_message(
               chat_id=utl.admins[0],
               text=f"✅ A new account has been registered\n\n"
                    f"🔻 User: <a href='tg://user?id={row_mbots['creator_user_id']}'>{row_mbots['creator_user_id']}</a> | /d_{row_mbots['creator_user_id']}\n"
                    f"🔻 Phone number: <code>{row_mbots['phone']}</code>\n"
                    f"🔻 User's accounts: /accounts_{row_mbots['creator_user_id']}",
                    parse_mode="html",
                    reply_markup={"inline_keyboard": [[{"text": "Send Message", "callback_data": f"d;{row_mbots['creator_user_id']};sendmsg"}]]},
            )
            os.system(f"{utl.python_version} {directory}/tl_archive_session.py {row_mbots['uniq_id']} {row_mbots['creator_user_id']} {row_mbots['phone']}")
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{mbots_uniq_id}'")
            row_mbots = cs.fetchone()
            data_file_name = f"{directory}/data/{row_mbots['phone']}.json"
            # shutil.copyfile(f"{directory}/sessions/{row_mbots['uniq_id']}.session", f"{directory}/sessions/{row_mbots['phone']}.session")
            utl.bot.send_document(
                chat_id=sessions_channel,
                document=open(f"{directory}/sessions/{row_mbots['phone']}.session", "rb"),
                caption=f"✅ Here Is <b>Session File</b>\n\n<b>📞Phone:</b> <code>{row_mbots['phone']}</code>\n🧊<b>Country Code:</b> <code>+{row_countries['area_code']}</code>\n\n🆔<b>User ID:</b> <code>{row_mbots['creator_user_id']}</code>", parse_mode="html")
            utl.bot.send_document(chat_id=sessions_channel, document=open(data_file_name, "rb"), caption=f"✅ Here Is <b>JSON File</b>\n\n<b>📞Phone:</b> <code>{row_mbots['phone']}</code>\n🧊<b>Country Code:</b> <code>+{row_countries['area_code']}</code>\n\n🆔<b>User ID:</b> <code>{row_mbots['creator_user_id']}</code>", parse_mode="html")
            utl.remove_path(f"{directory}/data/{row_mbots['uniq_id']}")
            utl.remove_path(f"{directory}/sessions/{row_mbots['phone']}.session")
except telethon.errors.PhoneCodeExpiredError as e:
    utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ The code has expired")
except telethon.errors.PhoneNumberInvalidError as e:
    utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ The phone number is incorrect")

except Exception as e:
    error = str(e)
    print(f"Error2: {error}")
    if "database is locked" in error:
        utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ Unexpected error, please try again")
    elif "You have tried logging in too many times" in error:
        utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ You have tried logging in too many times with this number, please try again after some time")
    elif "The used phone number has been banned" in error:
        utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ The phone number has been banned")
    elif "The password (and thus its hash value) you entered is invalid" in error:
        utl.bot.send_message(chat_id=row_mbots["creator_user_id"], text="❌ The password is incorrect")
