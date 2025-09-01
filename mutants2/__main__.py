import argparse
import os

from .cli.shell import main


def _parse_args() -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="enable dev mode")
    args = parser.parse_args()
    return args.dev or os.environ.get("MUTANTS2_DEV") == "1"


if __name__ == '__main__':
    dev_mode = _parse_args()
    main(dev_mode=dev_mode)
