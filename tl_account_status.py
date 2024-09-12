import os, re, sys, time, jdatetime, telethon, telethon.sync, utility as utl


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

cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{mbots_uniq_id}'")
row_mbots = cs.fetchone()

try:
    client = telethon.sync.TelegramClient(session=f"{directory}/sessions/{row_mbots['uniq_id']}", api_id=row_mbots['api_id'], api_hash=row_mbots['api_hash'])
    client.connect()
    if client.is_user_authorized():
        me = client.get_me()
        cs.execute(f"UPDATE {utl.mbots} SET user_id={int(me.id)},status=1 WHERE id={row_mbots['id']}")
        if type_ == 'scheck':
            utl.bot.send_message(chat_id=from_id,text="✅ Account is active")
        elif type_ == 'check':
            get_input_entity = client.get_input_entity(peer=777000)
            code = None
            for message in client.iter_messages(get_input_entity):
                try:
                    code_date = jdatetime.datetime.fromtimestamp(message.date.timestamp())
                    regex = re.findall('Login code: [\d]*. Do not give this code', message.message)[0]
                    code = regex.replace("Login code: ","").replace(". Do not give this code","")
                    break
                except:
                    pass
            code = f"<code>{code}</code>\n   📅 {code_date.strftime('%Y-%m-%d %H:%M:%S')}" if code is not None else "None"
            password = f"<code>{row_mbots['password']}</code>" if row_mbots['password'] is not None and row_mbots['password'] != '' else "None"
            photo = "No" if me.photo is None else "Yes"
            current_sessions = ""
            for session in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
                if session.current:
                    date_created = jdatetime.datetime.fromtimestamp(session.date_created.timestamp())
                    date_active = jdatetime.datetime.fromtimestamp(session.date_active.timestamp())
                    current_sessions += f"   🔻 IP: {session.ip}\n"
                    current_sessions += f"   🔻 Country: {session.country}\n"
                    current_sessions += f"   🔻 Device Model: {session.device_model}\n"
                    current_sessions += f"   🔻 Platform: {session.platform}\n"
                    current_sessions += f"   🔻 System Version: {session.system_version}\n"
                    current_sessions += f"   🔻 Api Id: <code>{session.api_id}</code>\n"
                    current_sessions += f"   🔻 App Name: {session.app_name}\n"
                    current_sessions += f"   🔻 App Version: {session.app_version}\n"
                    current_sessions += f"   🔻 Date Created: {date_created.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    current_sessions += f"   🔻 Date Active: {date_active.strftime('%Y-%m-%d %H:%M:%S')}\n"
            username = f"@{me.username}" if me.username is not None else "None"
            utl.bot.send_message(
                chat_id=from_id,
                text="✅ Account is active\n\n"
                    f"General:\n"
                    f"   🔻 Phone: <code>{me.phone}</code>\n"
                    f"   🔻 First Name: {me.first_name}\n"
                    f"   🔻 Last Name: {me.last_name}\n"
                    f"   🔻 Username: {username}\n"
                    f"   🔻 Photo: {photo}\n"
                    "\nCurrent Session:\n"
                    f"{current_sessions}"
                    f"\nPassword: {password}\n\n"
                    f"Last Login Code: {code}",
                parse_mode='HTML',
                reply_markup={'inline_keyboard': [[{'text': '❌ لاگ اوت ❌', 'callback_data': f"gc;logout;{row_mbots['id']};none"}]]}
            )
        elif type_ == 'sessions':
            i = 0
            for session in client(telethon.functions.account.GetAuthorizationsRequest()).authorizations:
                if not session.current:
                    i += 1
                    date_created = jdatetime.datetime.fromtimestamp(session.date_created.timestamp())
                    date_active = jdatetime.datetime.fromtimestamp(session.date_active.timestamp())
                    utl.bot.send_message(
                        chat_id=from_id,
                        text=f"Session {i}:\n"
                            f"   🔻 IP: {session.ip}\n"
                            f"   🔻 Country: {session.country}\n"
                            f"   🔻 Device Model: {session.device_model}\n"
                            f"   🔻 Platform: {session.platform}\n"
                            f"   🔻 System Version: {session.system_version}\n"
                            f"   🔻 Api Id: <code>{session.api_id}</code>\n"
                            f"   🔻 App Name: {session.app_name}\n"
                            f"   🔻 App Version: {session.app_version}\n"
                            f"   🔻 Date Created: {date_created.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"   🔻 Date Active: {date_active.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            "",
                        parse_mode='HTML'
                    )
    else:
        cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
        utl.bot.send_message(chat_id=from_id,text="❌ اکانت در دسترسی نیست")
except telethon.errors.PhoneNumberInvalidError as e:
    utl.bot.send_message(chat_id=from_id,text="❌ شماره اشتباه است")
except telethon.errors.FloodWaitError as e:
    utl.bot.send_message(chat_id=from_id,text=f"❌ شماره به مدت {utl.convert_time(e.seconds, 2)} محدود شده است")
except Exception as e:
    error = str(e)
    if "database is locked" in error:
        utl.bot.send_message(chat_id=from_id, text="❌ خطای غیر منتظره، دوباره تلاش کنید")
    elif "You have tried logging in too many times" in error:
        utl.bot.send_message(chat_id=from_id, text="❌ شما با این شماره بیش از حد تلاش کردید، بعد از مدتی مجدد تلاش کنید")
    elif "The used phone number has been banned" in error:
        utl.bot.send_message(chat_id=from_id, text="❌ شماره مسدود شده است")
    else:
        print(f"Error2: {error}")
        utl.bot.send_message(chat_id=from_id,text=f"❌ خطا\n\n{error}")
