# -*- coding: utf-8 -*-
# Copyright 2015 Tencent
# Author: Joe Lei <joelei@tencent.com>
import logging
import logging.config
import os.path
import time

from watchdog.observers import Observer

from autowatch import settings
from autowatch.events import AutoWatchYaml

logging.config.dictConfig(settings.LOGGING)
LOG = logging.getLogger(__name__)


def auto(tricks_file):
    LOG.info(tricks_file)
    if not os.path.exists(tricks_file):
        raise IOError("cannot find tricks file: %s" % tricks_file)
    tricks_file = os.path.abspath(tricks_file)
    dir_path = os.path.dirname(tricks_file)
    LOG.info(dir_path)
    event_handler = AutoWatchYaml(tricks_file)
    observer = Observer()
    observer.schedule(event_handler, dir_path, recursive=False)
    observer.start()
    LOG.info("Start AutoWatchYaml Success")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    LOG.error("AutoWatchYaml Stoped")
