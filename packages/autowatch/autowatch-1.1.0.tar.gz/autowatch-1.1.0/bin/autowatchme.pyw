# -*- coding: utf-8 -*-
# Copyright 2015 Tencent
# Author: Joe Lei <joelei@tencent.com>
import logging
import sys

from autowatch import cmd

LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "tricks_file is need."
        sys.exit(1)
    tricks_file = sys.argv[1]
    cmd.auto(tricks_file)
