"""
Tests for `clustercron` module.
"""

from clustercron import clustercron
import pytest


def test_opt_arg_parser_init():
    opt_arg_parser = clustercron.OptArgParser([])
    assert opt_arg_parser.arg_list == []
    assert opt_arg_parser.exitcode == 3
    assert opt_arg_parser.args == {
        'version': False,
        'help': False,
        'verbose': False,
        'dry_run': False,
        'lb_type': None,
        'lb_name': None,
        'command': [],
    }


def test_opt_arg_parser_usage():
    opt_arg_parser = clustercron.OptArgParser([])
    assert opt_arg_parser.usage == '''usage:  clustercron [options] elb <loadbalancer_name> <cron_command>
        clustercron [options] haproxy <loadbalancer_name> <cron_command>

-n      Dry-run, do not run <cron_command>
        shows where <cron_command> would have ran.
-v      Verbose output.

        clustercron --version
        clustercron (-h | --help)
'''


@pytest.mark.parametrize('arg_list,exitcode,args', [
    (
        [],
        3,
        {
            'version': False,
            'help': False,
            'verbose': False,
            'dry_run': False,
            'lb_type': None,
            'lb_name': None,
            'command': [],
        }
    ),
    (
        ['-h'],
        0,
        {
            'version': False,
            'help': True,
            'verbose': False,
            'dry_run': False,
            'lb_type': None,
            'lb_name': None,
            'command': [],
        }
    ),
    (
        ['--help'],
        0,
        {
            'version': False,
            'help': True,
            'verbose': False,
            'dry_run': False,
            'lb_type': None,
            'lb_name': None,
            'command': [],
        }
    ),
    (
        ['-v', '-n', 'elb', 'my_lb_name', 'update', '-r', 'thing'],
        0,
        {
            'version': False,
            'help': False,
            'verbose': True,
            'dry_run': True,
            'lb_type': 'elb',
            'lb_name': 'my_lb_name',
            'command': ['update', '-r', 'thing'],
        }
    ),
    (
        ['-n', 'haproxy', 'my_lb_name', 'update', '-r', 'thing'],
        0,
        {
            'version': False,
            'verbose': False,
            'help': False,
            'dry_run': True,
            'lb_type': 'haproxy',
            'lb_name': 'my_lb_name',
            'command': ['update', '-r', 'thing'],
        }
    ),
    (
        ['elb', '-n', 'my_lb_name', 'update', '-r', 'thing'],
        3,
        {
            'version': False,
            'help': False,
            'verbose': False,
            'dry_run': True,
            'lb_type': None,
            'lb_name': None,
            'command': [],
        }
    ),
    (
        ['haproxy', '-n', 'my_lb_name', 'update', '-r', 'thing'],
        3,
        {
            'version': False,
            'help': False,
            'verbose': False,
            'dry_run': True,
            'lb_type': None,
            'lb_name': None,
            'command': [],
        }
    ),
    # FIXME
    # (
    #     ['-v', 'haproxy', '-n', 'my_lb_name', 'update', '-r', 'thing'],
    #     3,
    #     {
    #         'version': False,
    #         'help': False,
    #         'verbose': False,
    #         'dry_run': False,
    #         'lb_type': None,
    #         'lb_name': None,
    #         'command': [],
    #     }
    # ),
])
def test_opt_arg_parser(arg_list, exitcode, args):
        opt_arg_parser = clustercron.OptArgParser(arg_list)
        opt_arg_parser.parse()
        assert opt_arg_parser.arg_list == arg_list
        assert opt_arg_parser.exitcode == exitcode
        assert opt_arg_parser.args == args
