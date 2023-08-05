import subprocess
import sys


def notify(message, sys=sys):
    if sys.platform == 'linux':
        subprocess.check_call(['notify-send', message])
    elif sys.platform == 'darwin':
        subprocess.check_call(['terminal-notifier', '-message', message])
    else:
        print(message)
