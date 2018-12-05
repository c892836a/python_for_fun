import os
# import re
import time
import psutil


# match = None
# while match is None:
#     hour = input('time to Interrupt (hours):')
#     match = re.match(r'^[1-9]\d*(\.\d*)?|0(\.\d*)?$', hour)

cmd1 = "cd /d \"C:\\Program Files\\rclone-v1.43.1-windows-amd64\""
cmd2 = "rclone copy \"D:\\資料相片\"" \
        + " \"gdrive:資料相片\" -v"
os.system("start cmd /c \"" + cmd1 + " & " + cmd2 + "\"")

second = int(float(6) * 3600)
time.sleep(second)

PROCNAME = "rclone.exe"
for proc in psutil.process_iter():
    # check whether the process name matches
    if proc.name() == PROCNAME:
        proc.kill()
