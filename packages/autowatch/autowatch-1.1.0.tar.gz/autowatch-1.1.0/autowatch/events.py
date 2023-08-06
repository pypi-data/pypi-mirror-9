# -*- coding: utf-8 -*-
# Copyright 2015 Tencent
# Author: Joe Lei <joelei@tencent.com>
import abc
import threading
import logging
import os

# from watchdog.utils import echo
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.watchmedo import (add_to_sys_path, load_config,
                                schedule_tricks, CONFIG_KEY_TRICKS,
                                CONFIG_KEY_PYTHON_PATH)

LOG = logging.getLogger(__name__)


class AutoWatchHandler(PatternMatchingEventHandler):

    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(AutoWatchHandler, self).__init__(*args, **kwargs)
        self.event = threading.Event()

    def start(self):
        w = self.watcher()
        w.start()

    def stop(self):
        self.event.set()

    # @echo.echo
    def on_any_event(self, event):
        self.stop()
        self.start()

    @abc.abstractmethod
    def watcher(self):
        """watcher
        """


class AutoWatchYaml(AutoWatchHandler):
    def __init__(self, files):
        patterns = ['*' + os.path.basename(files)]
        self.files = files
        LOG.info("PatternMatching: %s", patterns)
        super(AutoWatchYaml, self).__init__(patterns=patterns)

    def watcher(self):
        w = YamlTrick(self.event, [self.files])
        return w


class YamlTrick(threading.Thread):
    def __init__(self, event, files):
        super(YamlTrick, self).__init__()
        self.event = event
        self.event.clear()
        self.files = files

    def run(self):
        observers = []
        LOG.info("Start %s" % str(self))
        LOG.info('YamlTrick: %s', self.files)
        for tricks_file in self.files:
            observer = Observer(timeout=1)

            if not os.path.exists(tricks_file):
                raise IOError("cannot find tricks file: %s" % tricks_file)

            config = load_config(tricks_file)

            try:
                tricks = config[CONFIG_KEY_TRICKS]
            except KeyError:
                raise KeyError("No `%s' key specified in %s." % (
                               CONFIG_KEY_TRICKS, tricks_file))

            if CONFIG_KEY_PYTHON_PATH in config:
                add_to_sys_path(config[CONFIG_KEY_PYTHON_PATH])

            dir_path = os.path.dirname(tricks_file)
            if not dir_path:
                dir_path = os.path.relpath(os.getcwd())
            schedule_tricks(observer, tricks, dir_path, True)
            observer.start()
            observers.append(observer)

        self.event.wait()
        for o in observers:
            o.unschedule_all()
            o.stop()
        for o in observers:
            o.join()
        LOG.error("Stoped %s", str(self))
