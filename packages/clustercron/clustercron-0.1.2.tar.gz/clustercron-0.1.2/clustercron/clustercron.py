#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai

'''
Cluster Cron ============
'''

import logging
import sys


# general libary logging
logger = logging.getLogger(__name__)


class Clustercron(object):
    '''
    Main program class.
    Set properties from arguments.
    Runs sub commands in scopes.
    '''

    logger = logging.getLogger('clustercron')

    def __init__(self, args):
        self.args = args
        self.exitcode = 0
        print(self.args)
        # Run sub command in scope
        # getattr(self, self.args.cluster_type)()

    def run_command(self):
        pass


class OptArgParser(object):
    '''
    Parse command arguments
    Set properties from arguments.
    Runs sub commands in scopes.
    '''
    def __init__(self, arg_list):
        self.arg_list = arg_list
        # Set exitcode 3 for invalid arguments
        self.exitcode = 3
        self.args = {
            'version': False,
            'help': False,
            'verbose': False,
            'dry_run': False,
            'lb_type': None,
            'lb_name': None,
            'command': [],
        }

    @property
    def usage(self):
        res = 'usage:  clustercron [options] elb <loadbalancer_name>' \
            ' <cron_command>\n' \
            '        clustercron [options] haproxy <loadbalancer_name>' \
            ' <cron_command>\n\n' \
            '-n      Dry-run, do not run <cron_command>\n' \
            '        shows where <cron_command> would have ran.\n' \
            '-v      Verbose output.\n\n' \
            '        clustercron --version\n' \
            '        clustercron (-h | --help)\n'
        return res

    def parse(self):
        lb_type_index = 0
        if self.arg_list:
            if self.arg_list[0] == '-h' or self.arg_list[0] == '--help':
                self.args['help'] = True
                self.exitcode = 0
            if self.arg_list[0] == '--version':
                self.args['version'] = True
                self.exitcode = 0
            if '-v' in self.arg_list[:2]:
                self.args['verbose'] = True
                lb_type_index += 1
            if '-n' in self.arg_list[:2]:
                self.args['dry_run'] = True
                lb_type_index += 1
            if len(self.arg_list) > lb_type_index + 3 and \
                    (self.arg_list[lb_type_index] == 'elb' or
                     self.arg_list[lb_type_index] == 'haproxy'):
                self.args['lb_type'] = self.arg_list[lb_type_index]
                self.args['lb_name'] = self.arg_list[lb_type_index + 1]
                self.args['command'] = self.arg_list[lb_type_index + 2:]
                self.exitcode = 0


def setup_logging(verbose):
    # Set Level for console handler
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    # Set up Console Handler
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(
        logging.Formatter(fmt='%(levelname)-8s %(name)s : %(message)s')
    )
    handler_console.setLevel(log_level)
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    # Add Handlers
    root_logger.addHandler(handler_console)


def main():
    '''
    Entry point for the package, as defined in setup.py.
    '''
    # Parse args
    opt_arg_parser = OptArgParser(sys.argv[1:])
    opt_arg_parser.parse()
    if opt_arg_parser.exitcode != 0:
        print(opt_arg_parser.usage)
        sys.exit(opt_arg_parser.exitcode)
    # Logging
    setup_logging(opt_arg_parser.args['verbose'])
    # Args
    logger.debug('Command line arguments: %s', opt_arg_parser.args)
    sys.exit(Clustercron(opt_arg_parser.args).exitcode)


if __name__ == '__main__':
    main()
