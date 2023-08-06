# -*- coding: utf-8 -*-
# Copyright 2015 Tencent
# Author: Joe Lei <joelei@tencent.com>
import os.path

ROOT_PACKAGE = __name__.split('.')[0]
PATH = os.path.abspath('.')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PATH, 'autowatch.log'),
            'formatter': 'simple'
        }
    },
    'loggers': {
        ROOT_PACKAGE: {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '__main__': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
