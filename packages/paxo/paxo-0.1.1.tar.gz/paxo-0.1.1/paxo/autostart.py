"""
paxo.autostart - the magic every day
"""

import os

from paxo.util import is_lin, is_win, is_osx, ExitStatus

if is_lin:
    from crontab import CronTab

""" example call

def auto_upload():
    response = auto_task("com.cwoebker", "como-upload", ((11, 0))
                 os.popen('which como').read().rstrip('\n')):
    if reponse is ExitStatus.NOTSUPPORTED:
        error("como is not supported on your operating system")
    elif reponse:
        info("como will automatically upload the data")
    else:
        info("como will not upload data")
        """


def auto_task(identifier, name, time_list, argument_list, program_path):
    if is_win:
        return ExitStatus.NOTSUPPORTED
    elif is_osx:

        time_string = ""
        for time in time_list:
            time_string += """<key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
        """.format(hour=time[0], minute=time[1])

        argument_string = ""
        for arg in argument_list:
            argument_string += """<string>{arg}</string>
        """.format(arg=arg)

        apple_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" """ + \
            """ "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{identifier}.{name}</string>
    <key>OnDemand</key>
    <true/>
    <key>RunAtLoad</key>
    <false/>
    <key>ProgramArguments</key>
    <array>
        <string>{program_path}</string>
        {argument_string}
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        {time_string}
    </dict>
</dict>
</plist>
""".format(identifier=identifier, name=name, time_string=time_string,
           argument_string=argument_string, program_path=program_path)

        plist_path = os.path.expanduser(
            "~/Library/LaunchAgents/{identifier}.{name}")

        if os.path.exists(plist_path):
            os.system("launchctl unload %s" % plist_path)
            os.remove(plist_path)
            return False
        else:
            with open(plist_path, "w") as plist_file:
                plist_file.write(apple_plist)
            os.system("launchctl load %s" % plist_path)
            return True
    elif is_lin:
        user_cron = CronTab()
        user_cron.read()
        if len(user_cron.find_command(name)) > 0:
            user_cron.remove_all(name)
            user_cron.write()
            return False
        else:
            job = user_cron.new(command=name)
            job.minute.every(2)
            user_cron.write()
            return True
