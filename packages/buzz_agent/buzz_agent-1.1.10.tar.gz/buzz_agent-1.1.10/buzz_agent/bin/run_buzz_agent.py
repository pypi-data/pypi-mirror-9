#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import argparse
import logging
import logging.config
import buzz_agent
from buzz_agent import BuzzAgent


# 日志
# 为了保证邮件只有在正式环境发送
class RequireDebugOrNot(logging.Filter):
    _need_debug = False

    def __init__(self, need_debug, *args, **kwargs):
        super(RequireDebugOrNot, self).__init__(*args, **kwargs)
        self._need_debug = need_debug

    def filter(self, record):
        return debug if self._need_debug else not debug


LOG_FILE_PATH = "/tmp/buzz_agent.log"

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
        'flylog': {
            'level': 'CRITICAL',
            'class': 'flylog.FlyLogHandler',
            'formatter': 'standard',
            'source': 'svdog',
        },
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
        'default': {
            'handlers': ['console', 'rotating_file', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'svdog': {
            'handlers': ['console', 'rotating_file', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

# 全局的
debug = False
logger = logging.getLogger('default')


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='path', required=True)
    parser.add_argument('-m', '--domain', help='domain, like 192.168.1.10:8000 or xx.com', required=True)
    parser.add_argument('-s', '--secret', help='secret', required=True)
    parser.add_argument('-i', '--interval', help='interval seconds', type=int, required=True)
    parser.add_argument('-d', '--debug', default=False, help='debug mode', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%s' % buzz_agent.__version__)

    return parser


def configure_logging():
    logging.config.dictConfig(LOGGING)


def process(path, domain, secret, interval):
    """
    执行
    """

    agent = BuzzAgent(path, domain, secret, interval)

    while True:
        try:
            agent.run()
        except KeyboardInterrupt:
            break
        except:
            logger.error('exc occur.', exc_info=True)

        time.sleep(interval)


def main():
    global debug

    configure_logging()

    args = build_parser().parse_args()
    debug = args.debug

    try:
        process(args.path, args.domain, args.secret, args.interval)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()