import pytest
import sys
import numpy as np
from srcs import snake


def dict_to_argv(file, arg_dict):
    argv = [file]
    store_true_options = {"eval"}

    for key, value in arg_dict.items():
        if value is None:
            continue
        if key in store_true_options:
            if value:
                argv.append(f'-{key}')
        else:
            argv.append(f'-{key}')
            argv.append(str(value))
    return argv


class TestSnakeArgument:
    @classmethod
    def setup_class(cls):
        cls.base_args = {
            "visual"  : "on",
            "load"    : "test_load",
            "save"    : "test_save",
            "sessions": "10",
            "eval"    : False,
        }
        cls.filename = 'snake.py'

    def test_snake_arguments(self):
        sys.argv = dict_to_argv(self.filename, self.base_args)
        args = snake.parse_arguments()
        assert args.visual == "on"
        assert args.load == "test_load"
        assert args.save == "test_save"
        assert args.sessions == 10
        assert not args.eval

    @pytest.mark.parametrize("field, value, expected_error", [
        ("visual",  "",            SystemExit),
        ("visual",  " ",           SystemExit),
        ("visual",  "nothing",     SystemExit),

        ("sessions", "",        SystemExit),
        ("sessions", "-10",     SystemExit),
        ("sessions", "0",       SystemExit),
        ("sessions", "10001",   SystemExit),
        ("sessions", "2147483647",           SystemExit),
        ("sessions", "2147483648",           SystemExit),
        ("sessions", "-2147483648",          SystemExit),
        ("sessions", "-2147483649",          SystemExit),
        ("sessions", "9223372036854775807",  SystemExit),
        ("sessions", "9223372036854775808",  SystemExit),
        ("sessions", "-9223372036854775808", SystemExit),
        ("sessions", "-9223372036854775809", SystemExit),
        ("sessions", " ",     SystemExit),
        ("sessions", "a",     SystemExit),
        ("sessions", "10a",   SystemExit),
        ("sessions", "1e100", SystemExit), ])
    def test_invalid_arguments(self, field, value, expected_error):
        invalid_args = self.base_args.copy()
        invalid_args[field] = value
        sys.argv = dict_to_argv(self.filename, invalid_args)
        with pytest.raises(expected_error):
            snake.parse_arguments()

    @pytest.mark.parametrize("field, value, expected", [
        ("visual",  "on",   "on"),
        ("visual",  "ON",   "on"),
        ("visual",  "On",   "on"),
        ("visual",  "off",  "off"),
        ("visual",  "OFF",  "off"),
        ("visual",  "OfF",  "off"),

        ("sessions",    "1",      1),
        ("sessions",    "10",     10),
        ("sessions",    "100",    100),
        ("sessions",    "1000",   1000),
        ("sessions",    "10000",  10000), ])
    def test_valid_argument_variations(self, field, value, expected):
        valid_args = self.base_args.copy()
        valid_args[field] = value
        sys.argv = dict_to_argv(self.filename, valid_args)
        args = snake.parse_arguments()
        assert getattr(args, field) == expected
