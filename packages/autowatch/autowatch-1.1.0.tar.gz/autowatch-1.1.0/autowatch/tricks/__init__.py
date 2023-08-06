# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import subprocess
import os
import logging

from watchdog.tricks import Trick
from watchdog.utils import has_attribute

LOG = logging.getLogger(__name__)


class Rsync(Trick):
    """Rsync Trick
    """

    def __init__(self, shell_command=None, patterns=None, ignore_patterns=None,
                 ignore_directories=False, wait_for_process=False,
                 drop_during_process=True, **kwargs):
        super(Rsync, self).__init__(patterns, ignore_patterns, ignore_directories)
        self.shell_command = shell_command
        if not self.shell_command:
            self.shell_command = 'rsync -avz ${source_directory} %s' % kwargs.get('target')
        self.wait_for_process = wait_for_process
        self.drop_during_process = drop_during_process
        self.process = None
        self.kwargs = kwargs
        self.source_directory = kwargs.get('source_directory')
        os.environ['RSYNC_PASSWORD'] = 'joelei123'

    def on_any_event(self, event):
        from string import Template

        if self.drop_during_process and self.process and self.process.poll() is None:
            return

        if event.is_directory:
            object_type = 'directory'
        else:
            object_type = 'file'

        context = {
            'watch_src_path': event.src_path,
            'watch_dest_path': '',
            'watch_event_type': event.event_type,
            'watch_object': object_type,
        }

        if self.shell_command is None:
            if has_attribute(event, 'dest_path'):
                context.update({'dest_path': event.dest_path})
                command = 'echo "${watch_event_type} ${watch_object} from ${watch_src_path} to ${watch_dest_path}"'
            else:
                command = 'echo "${watch_event_type} ${watch_object} ${watch_src_path}"'
        else:
            if has_attribute(event, 'dest_path'):
                context.update({'watch_dest_path': event.dest_path})
            command = self.shell_command
        context.update(self.kwargs)
        driver, path = self.source_directory.split(':')
        context['source_directory'] = '/cygdrive/%s%s' % (driver.lower(), path.replace('\\', '/'))

        command = Template(command).safe_substitute(**context)
        if self.ignore_directories:
            for i in self.ignore_directories:
                command += ' --exclude %s ' % i

        LOG.info(">>> %s" % command)
        self.process = subprocess.Popen(command, shell=True)
        if self.wait_for_process:
            self.process.wait()
