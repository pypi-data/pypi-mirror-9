from .parse_args import parse_args
from .run import run
import sys


def main():
    settings = parse_args(sys.argv[1:])
    run(settings)
