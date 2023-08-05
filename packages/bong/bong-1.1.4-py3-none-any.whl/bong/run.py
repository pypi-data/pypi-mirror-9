import time
from .notify import notify


def run(settings, sleep=time.sleep, notify=notify):
    sleep(settings.time)
    notify(settings.message)
