# -*- coding: utf-8 -*-
"""\
Test the natsort command-line tool functions.
"""
from __future__ import print_function
import re
import sys
from pytest import raises
try:
    from unittest.mock import patch, call
except ImportError:
    from mock import patch, call
from natsort.__main__ import main, range_check, check_filter
from natsort.__main__ import keep_entry_range, exclude_entry
from natsort.__main__ import sort_and_print_entries


def test_main_passes_default_arguments_with_no_command_line_options():
    with patch('natsort.__main__.sort_and_print_entries') as p:
        sys.argv[1:] = ['num-2', 'num-6', 'num-1']
        main()
        args = p.call_args[0][1]
        assert not args.paths
        assert args.filter is None
        assert args.reverse_filter is None
        assert args.exclude is None
        assert not args.reverse
        assert args.number_type == 'float'
        assert args.signed
        assert args.exp
        assert not args.locale


def test_main_passes_arguments_with_all_command_line_options():
    with patch('natsort.__main__.sort_and_print_entries') as p:
        sys.argv[1:] = ['--paths', '--reverse', '--locale',
                        '--filter', '4', '10',
                        '--reverse-filter', '100', '110',
                        '--number-type', 'int',
                        '--nosign', '--noexp',
                        '--exclude', '34', '--exclude', '35',
                        'num-2', 'num-6', 'num-1']
        main()
        args = p.call_args[0][1]
        assert args.paths
        assert args.filter == [(4.0, 10.0)]
        assert args.reverse_filter == [(100.0, 110.0)]
        assert args.exclude == [34, 35]
        assert args.reverse
        assert args.number_type == 'int'
        assert not args.signed
        assert not args.exp
        assert args.locale


def test_range_check_returns_range_as_is_but_with_floats():
    assert range_check(10, 11) == (10.0, 11.0)
    assert range_check(6.4, 30) == (6.4, 30.0)


def test_range_check_raises_ValueError_if_range_is_invalid():
    with raises(ValueError) as err:
        range_check(7, 2)
    assert str(err.value) == 'low >= high'


def test_check_filter_returns_None_if_filter_evaluates_to_False():
    assert check_filter(()) is None
    assert check_filter(False) is None
    assert check_filter(None) is None


def test_check_filter_converts_filter_numbers_to_floats_if_filter_is_valid():
    assert check_filter([(6, 7)]) == [(6.0, 7.0)]
    assert check_filter([(6, 7), (2, 8)]) == [(6.0, 7.0), (2.0, 8.0)]


def test_check_filter_raises_ValueError_if_filter_is_invalid():
    with raises(ValueError) as err:
        check_filter([(7, 2)])
    assert str(err.value) == 'Error in --filter: low >= high'


def test_keep_entry_range_returns_True_if_any_portion_of_input_is_between_the_range_bounds():
    assert keep_entry_range('a56b23c89', [0], [100], int, re.compile(r'\d+'))


def test_keep_entry_range_returns_True_if_any_portion_of_input_is_between_any_range_bounds():
    assert keep_entry_range('a56b23c89', [1, 88], [20, 90], int, re.compile(r'\d+'))


def test_keep_entry_range_returns_False_if_no_portion_of_input_is_between_the_range_bounds():
    assert not keep_entry_range('a56b23c89', [1], [20], int, re.compile(r'\d+'))


def test_exclude_entry_returns_True_if_exlcude_parameters_are_not_in_input():
    assert exclude_entry('a56b23c89', [100, 45], int, re.compile(r'\d+'))


def test_exclude_entry_returns_False_if_exlcude_parameters_are_in_input():
    assert not exclude_entry('a56b23c89', [23], int, re.compile(r'\d+'))


class Args:
    """A dummy class to simulate the argparse Namespace object"""
    def __init__(self, filter, reverse_filter, exclude, as_path, reverse):
        self.filter = filter
        self.reverse_filter = reverse_filter
        self.exclude = exclude
        self.reverse = reverse
        self.number_type = 'float'
        self.signed = True
        self.exp = True
        self.paths = as_path
        self.locale = 0

entries = ['tmp/a57/path2',
           'tmp/a23/path1',
           'tmp/a1/path1',
           'tmp/a1 (1)/path1',
           'tmp/a130/path1',
           'tmp/a64/path1',
           'tmp/a64/path2']

mock_print = '__builtin__.print' if sys.version[0] == '2' else 'builtins.print'


def test_sort_and_print_entries_uses_default_algorithm_with_all_options_false():
    with patch(mock_print) as p:
        # tmp/a1 (1)/path1
        # tmp/a1/path1
        # tmp/a23/path1
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        # tmp/a130/path1
        sort_and_print_entries(entries, Args(None, None, False, False, False))
        e = [call(entries[i]) for i in [3, 2, 1, 0, 5, 6, 4]]
        p.assert_has_calls(e)


def test_sort_and_print_entries_uses_PATH_algorithm_with_path_option_true_to_properly_sort_OS_generated_path_names():
    with patch(mock_print) as p:
        # tmp/a1/path1
        # tmp/a1 (1)/path1
        # tmp/a23/path1
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        # tmp/a130/path1
        sort_and_print_entries(entries, Args(None, None, False, True, False))
        e = [call(entries[i]) for i in [2, 3, 1, 0, 5, 6, 4]]
        p.assert_has_calls(e)


def test_sort_and_print_entries_keeps_only_paths_between_of_20_to_100_with_filter_option():
    with patch(mock_print) as p:
        # tmp/a23/path1
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        sort_and_print_entries(entries, Args([(20, 100)], None, False, False, False))
        e = [call(entries[i]) for i in [1, 0, 5, 6]]
        p.assert_has_calls(e)


def test_sort_and_print_entries_excludes_paths_between_of_20_to_100_with_reverse_filter_option():
    with patch(mock_print) as p:
        # tmp/a1/path1
        # tmp/a1 (1)/path1
        # tmp/a130/path1
        sort_and_print_entries(entries, Args(None, [(20, 100)], False, True, False))
        e = [call(entries[i]) for i in [2, 3, 4]]
        p.assert_has_calls(e)


def test_sort_and_print_entries_excludes_paths_23_or_130_with_exclude_option_list():
    with patch(mock_print) as p:
        # tmp/a1/path1
        # tmp/a1 (1)/path1
        # tmp/a57/path2
        # tmp/a64/path1
        # tmp/a64/path2
        sort_and_print_entries(entries, Args(None, None, [23, 130], True, False))
        e = [call(entries[i]) for i in [2, 3, 0, 5, 6]]
        p.assert_has_calls(e)


def test_sort_and_print_entries_reverses_order_with_reverse_option():
    with patch(mock_print) as p:
        # tmp/a130/path1
        # tmp/a64/path2
        # tmp/a64/path1
        # tmp/a57/path2
        # tmp/a23/path1
        # tmp/a1 (1)/path1
        # tmp/a1/path1
        sort_and_print_entries(entries, Args(None, None, False, True, True))
        e = [call(entries[i]) for i in reversed([2, 3, 1, 0, 5, 6, 4])]
        p.assert_has_calls(e)
