import sys

from pygate.argparser import create_root_parser, parse_env_file_path


class TestCreateRootParser:
    def test_env_file_defaults_to_none(self):
        parser = create_root_parser()
        args = parser.parse_args([])
        assert args.env_file is None

    def test_parses_env_file_flag(self):
        parser = create_root_parser()
        args = parser.parse_args(["--env-file", "custom.env"])
        assert args.env_file == "custom.env"

    def test_unknown_flags_are_not_swallowed_by_parse_args(self):
        # The plain parser should reject arguments it doesn't understand, e.g. Settings' own --host/--port.
        parser = create_root_parser()
        try:
            parser.parse_args(["--host", "1.2.3.4"])
        except SystemExit:
            pass
        else:
            raise AssertionError("expected SystemExit for an unrecognized argument")