#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动 flylog_agent
"""

import imp
import errno
import argparse
import os.path as op
import logging
import logging.config

import sys
import flylog
from flylog import FlyLogAgent
from flylog import constants


# 日志
# 为了保证邮件只有在正式环境发送
class RequireDebugOrNot(logging.Filter):
    _need_debug = False

    def __init__(self, need_debug, *args, **kwargs):
        super(RequireDebugOrNot, self).__init__(*args, **kwargs)
        self._need_debug = need_debug

    def filter(self, record):
        return debug if self._need_debug else not debug


LOG_FILE_PATH = "/tmp/flylog_agent.log"

LOG_FORMAT = '\n'.join((
    '/' + '-' * 80,
    '[%(levelname)s][%(asctime)s][%(process)d:%(thread)d][%(filename)s:%(lineno)d %(funcName)s]:',
    '%(message)s',
    '-' * 80 + '/',
))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'standard': {
            'format': LOG_FORMAT,
        },
    },

    'filters': {
        'require_debug_false': {
            '()': RequireDebugOrNot,
            'need_debug': False,
        },
        'require_debug_true': {
            '()': RequireDebugOrNot,
            'need_debug': True,
        },
    },

    'handlers': {
        'rotating_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['require_debug_true'],
        },
    },

    'loggers': {
        'flylog': {
            'handlers': ['console', 'rotating_file'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}


logger = logging.getLogger('flylog')
debug = False


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--host', default=constants.AGENT_HOST, help='bind host', action='store')
    parser.add_argument('-p', '--port', default=constants.AGENT_PORT, type=int, help='bind port', action='store')
    parser.add_argument('-c', '--config', help='config file', action='store', required=True)
    parser.add_argument('-d', '--debug', default=False, help='debug mode', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%s' % flylog.__version__)
    return parser


def configure_logging():
    logging.config.dictConfig(LOGGING)


def load_config(filename):
    d = imp.new_module('config')
    d.__file__ = filename
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
    except IOError as e:
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return d


def run_flylog_agent():
    global debug

    configure_logging()

    args = build_parser().parse_args()

    prog = FlyLogAgent(config=load_config(args.config))

    # 设置到全局配置里
    debug = prog.debug = args.debug

    logger.info("Running FlyLogAgent on %(host)s:%(port)s, config:%(config)s, debug:%(debug)s" % dict(
        host=args.host, port=args.port, config=args.config, debug=args.debug)
    )

    try:
        prog.run(args.host, args.port)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    run_flylog_agent()
