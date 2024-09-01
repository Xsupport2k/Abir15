import os, time, utility as utl

directory = os.path.dirname(os.path.abspath(__file__))
filename = str(os.path.basename(__file__))

utl.get_params_pids_by_full_script_name(script_names=[f"{directory}/{filename}"], is_kill_proccess=True)
print(f"ok: {filename}")


while True:
    try:
        timestamp = int(time.time())

        cs = utl.Database()
        cs = cs.data()

        cs.execute(f"SELECT * FROM {utl.admin}")
        row_admin = cs.fetchone()
        
        cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND ({timestamp}-last_update_status_at)>172800")
        result = cs.fetchall()
        for row_mbots in result:
            os.system(f"{utl.python_version} \"{directory}/tl_settings.py\" {row_mbots['uniq_id']} update_status_at")
        if row_admin['change_pass']:
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND is_change_pass=0 AND ({timestamp}-change_pass_at)>43200")
            result = cs.fetchall()
            for row_mbots in result:
                os.system(f"{utl.python_version} \"{directory}/tl_settings.py\" {row_mbots['uniq_id']} change_password")
        if row_admin['is_change_profile']:
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND is_change_profile=0")
            result = cs.fetchall()
            for row_mbots in result:
                os.system(f"{utl.python_version} \"{directory}/tl_settings.py\" {row_mbots['uniq_id']} change_profile")
        if row_admin['is_set_username']:
            cs.execute(f"SELECT * FROM {utl.mbots} WHERE status>0 AND is_set_username=0")
            result = cs.fetchall()
            for row_mbots in result:
                os.system(f"{utl.python_version} \"{directory}/tl_settings.py\" {row_mbots['uniq_id']} set_username")
    except:
        pass
    time.sleep(60)
