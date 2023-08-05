import subprocess

def notify(message):
    subprocess.check_call(['notify-send', message])
