from .settings import BongSettings, DEFAULT_MESSAGE
from .metadata import VERSION, SUMMARY
import argparse

PARSER = argparse.ArgumentParser(description=SUMMARY)
PARSER.add_argument('-V', '--version', action='version', version=VERSION,
                    help='Show version')
PARSER.add_argument('-s', '--short-break', action='store_const', const=5,
                    dest='minutes', default=25,
                    help='Time for a Pomodoro system short break')
PARSER.add_argument('-l', '--long-break', action='store_const',
                    const=15, dest='minutes',
                    help='Time for a Pomodoro system long break')
PARSER.add_argument('-p', '--pomodoro', action='store_const',
                    const=25, dest='minutes',
                    help='Time for a Pomodoro system single Pomodoro')
PARSER.add_argument('-t', '--time', action='store', type=int, dest='minutes',
                    help='Timer length, in minutes')
PARSER.add_argument('-m', '--message', default=DEFAULT_MESSAGE,
                    help='Message to display in the notifier')


def parse_args(args):
    settings = PARSER.parse_args(args)
    return BongSettings(time=60*settings.minutes, message=settings.message)
