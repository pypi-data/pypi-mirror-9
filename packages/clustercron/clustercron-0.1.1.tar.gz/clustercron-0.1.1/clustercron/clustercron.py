#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai

'''
Cluster Cron
============
'''

import argparse
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
        # Run sub command in scope
        # getattr(self, self.args.scope)()


def parse_clustercron_args(args):
    '''
    Parse the command-line arguments to clustercron
    '''
    # Create top-level parser
    parser = argparse.ArgumentParser(
        prog='clustercron',
        description='Cron job wrapper that ensures a script gets run from one '
        'node in the cluster.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Add options to top-level parser
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Show verbose info (level DEBUG).',
    )
    # Create sub parsers
    parser_cluster_type = parser.add_subparsers(
        help='Cluster type',
        dest='cluster_type',
    )
    # Add 'elb cluster type'
    parser_cluster_type_ELB = parser_cluster_type.add_parser(
        'ELB',
        help='Scope AWS Elastic Load Balance',
    )
    # Add command argument to 'ielb cluster type'
    parser_cluster_type_ELB.add_argument(
        'command',
        help='Cron job command'
    )
    return parser.parse_args(args)


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
    args = parse_clustercron_args(sys.argv[1:])
    # Logging
    setup_logging(args.verbose)
    # Args
    logger.debug('Command line arguments: %s', args)
    sys.exit(Clustercron(args).exitcode)


if __name__ == '__main__':
    main()
