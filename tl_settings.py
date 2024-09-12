import os, sys, time, glob, random, telethon.sync, utility as utl


for index, arg in enumerate(sys.argv):
    if index == 1:
        mbots_uniq_id = arg
    elif index == 2:
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
    if client.is_user_authorized():
        if type_ == 'update_status_at':
            cs.execute(f"UPDATE {utl.mbots} SET last_update_status_at={timestamp} WHERE id={row_mbots['id']}")
            client(telethon.functions.messages.SendMessageRequest(peer='me', message='online!'))
            print(f"{row_mbots['phone']} : Update OK")
        elif type_ == 'change_password':
            cs.execute(f"UPDATE {utl.mbots} SET change_pass_at={timestamp} WHERE id={row_mbots['id']}")
            try:
                new_password = row_admin['account_password']
                if row_mbots['password'] is None or row_mbots['password'] == '':
                    client.edit_2fa(new_password=new_password)
                else:
                    client.edit_2fa(current_password=row_mbots['password'], new_password=new_password)
                cs.execute(f"UPDATE {utl.mbots} SET password='{new_password}',is_change_pass=1 WHERE id={row_mbots['id']}")
                print(f"{row_mbots['phone']} : Password OK")
            except Exception as e:
                if "you entered is invalid" in str(e):
                    print(f"{row_mbots['phone']}: Password Invalid")
                    cs.execute(f"UPDATE {utl.mbots} SET is_change_pass=1 WHERE id={row_mbots['id']}")
                else:
                    print(f"Error Password: {e}")
        elif type_ == 'change_profile':
            files = glob.glob(f"{directory}/images/*.jpg")
            files_length = len(files) - 1
            client(telethon.functions.account.UpdateProfileRequest(first_name=utl.name_list[random.randint(0, (len(utl.name_list) - 1))], last_name='', about=utl.about_list[random.randint(0, (len(utl.about_list) - 1))]))
            client(telethon.functions.photos.UploadProfilePhotoRequest(file=client.upload_file(files[random.randint(0, files_length)])))
            client(telethon.functions.photos.UploadProfilePhotoRequest(file=client.upload_file(files[random.randint(0, files_length)])))
            cs.execute(f"UPDATE {utl.mbots} SET is_change_profile=1 WHERE id={row_mbots['id']}")
            print(f"{row_mbots['phone']} : Profile OK")
        elif type_ == 'set_username':
            client(telethon.functions.account.UpdateUsernameRequest(username=utl.username_list[random.randint(0, (len(utl.username_list) - 1))] + utl.random_generate(10)))
            cs.execute(f"UPDATE {utl.mbots} SET is_set_username=1 WHERE id={row_mbots['id']}")
            print(f"{row_mbots['phone']} : Username OK")
    else:
        cs.execute(f"UPDATE {utl.mbots} SET status=0 WHERE id={row_mbots['id']}")
except Exception as e:
    print(e)
    