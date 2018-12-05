import psutil
import os
import subprocess


PROCNAME = "PIMELauncher.exe"

for proc in psutil.process_iter():
    # check whether the process name matches
    if proc.name() == PROCNAME:
        proc.kill()

subprocess.Popen(
    os.environ["ProgramFiles(x86)"] + "\\PIME\\PIMELauncher.exe")
