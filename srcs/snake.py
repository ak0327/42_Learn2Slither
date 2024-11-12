import sys
import argparse

from distutils.util import strtobool
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from srcs.modules.parser import str_expected, int_expected


def main(random_state: int = 42):
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Snake"
    )
    parser.add_argument(
        "-visual",
        type=str_expected(["on", "off"]),
        default="on",
        help="visual on or off"
    )
    parser.add_argument(
        "-load",
        type=str,
        help="Path to model load"
    )
    parser.add_argument(
        "-save",
        type=str,
        help="Path to model save"
    )
    parser.add_argument(
        "-sessions",
        type=int_expected([1, 10, 100]),
        default=10,
        help="Path to model save"
    )
    parser.add_argument(
        "-eval",
        type=strtobool,
        default=0,
        help="Eval mode: true or false"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    print(f"args:")
    print(f" visual  : {args.visual}")
    print(f" load    : {args.load}")
    print(f" save    : {args.save}")
    print(f" sessions: {args.sessions}")
    print(f" eval    : {bool(args.eval)}")
    main()
