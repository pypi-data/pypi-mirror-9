#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2012, GoodData(R) Corporation. All rights reserved

"""
Initialize GDC logging

Initialize:
import gdc.logger
import logging
gdc.logger.init()
lg = logging.getLogger('gdc.application')
lg.info("Logger loaded")

Usage:
import logging
lg = logging.getLogger('gdc.application')
"""

import logging
import logging.handlers
import socket
from sgmanager.logger.level_handler import LevelHandler

lg = None

# Initialize logging
def init(name='', level=logging.WARN, syslog=True, console=True):
    global lg

    lg = logging.getLogger(name)
    lg.setLevel(level)

    if console:
        lg_console = LevelHandler()
        lg_console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

        lg.addHandler(lg_console)

    if syslog:
        lg_syslog = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_LOCAL5, address=(socket.gethostname(), 514))
        lg_syslog.setFormatter(logging.Formatter('%(name)-9s %(levelname)-8s %(message)s'))

        lg.addHandler(lg_syslog)

    return lg
