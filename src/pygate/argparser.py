import argparse
from typing import cast


def create_root_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-file",
        dest="env_file",
        type=str,
        default=None,
        metavar="str",
        help="Path to env file (default: .env) [env: PYGATE_ENV_FILE]",
    )
    return parser


def parse_env_file_path(parser: argparse.ArgumentParser) -> str | None:
    args, extra = parser.parse_known_args()
    return cast(str | None, args.env_file)
