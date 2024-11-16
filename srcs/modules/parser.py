import argparse
import os
import numpy as np


def str_expected(expected_strs: list[str]):
    lower_list = [s.lower() for s in expected_strs]

    def _checker(arg):
        s = arg.lower()
        if s not in lower_list:
            raise argparse.ArgumentTypeError(
                f"{arg} is not expected: {lower_list}"
            )
        return s
    return _checker


def int_expected(expected_nums: list[int]):
    def _checker(arg):
        try:
            value = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{arg} is not a valid integer")
        if value not in expected_nums:
            raise argparse.ArgumentTypeError(f"{arg} is not expected: {expected_nums}")
        return value
    return _checker


def validate_extention(expected_ext: list[str]):
    extensions = [ext.lower() for ext in expected_ext]

    def _checker(arg):
        filename = arg.lower()
        if any(filename.endswith(ext) for ext in extensions):
            return arg
        raise argparse.ArgumentTypeError(f"{arg} is not expected: {extensions}")
    return _checker


def int_range(min_val, max_val):
    def _checker(arg):
        try:
            value = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{arg} is not a valid integer")
        if value < min_val or max_val < value:
            raise argparse.ArgumentTypeError(
                f"{value} is not in range [{min_val}, {max_val}]"
            )
        return value
    return _checker


def float_range(min_val, max_val):
    def _checker(arg):
        try:
            value = float(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{arg} is not a valid float")
        if np.isnan(value):
            raise argparse.ArgumentTypeError(f"{arg} is NaN")
        if value < min_val or max_val < value:
            raise argparse.ArgumentTypeError(
                f"{value} is not in range [{min_val}, {max_val}]"
            )
        return value
    return _checker


def float_range_exclusive(min_val, max_val):
    def _checker(arg):
        try:
            value = float(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{arg} is not a valid float")
        if np.isnan(value):
            raise argparse.ArgumentTypeError(f"{arg} is NaN")
        if value <= min_val or max_val <= value:
            raise argparse.ArgumentTypeError(
                f"{value} is not in range ({min_val}, {max_val})"
            )
        return value
    return _checker


def int_list_type(min_elements, max_elements, min_value, max_value):
    def _checker(arg):
        if isinstance(arg, str):
            values = arg.split()
        elif isinstance(arg, list):
            values = arg
        else:
            raise argparse.ArgumentTypeError(
                "Invalid input type for hidden_features"
            )

        try:
            values = [int(v) for v in values]
        except ValueError:
            raise argparse.ArgumentTypeError(
                "All elements of hidden_features must be integers"
            )

        if not (min_elements <= len(values) <= max_elements):
            raise argparse.ArgumentTypeError(
                f"Must have {min_elements} to {max_elements} elements"
            )

        if any(value < min_value or max_value < value for value in values):
            raise argparse.ArgumentTypeError(
                f"All values in hidden_features must be between {min_value} and {max_value}"
            )

        return values
    return _checker


def valid_dir(s):
    if s is None:
        raise argparse.ArgumentTypeError("Must be not None")
    if not isinstance(s, str):
        raise argparse.ArgumentTypeError(f"Must be a string: {s}")
    if not os.path.exists(s):
        raise argparse.ArgumentTypeError(f"Directory not found: {s}")
    if not os.path.isdir(s):
        raise argparse.ArgumentTypeError(f"Not a directory: {s}")
    if not os.access(s, os.W_OK):
        raise argparse.ArgumentTypeError(f"Directory not writable: {s}")
    return s
