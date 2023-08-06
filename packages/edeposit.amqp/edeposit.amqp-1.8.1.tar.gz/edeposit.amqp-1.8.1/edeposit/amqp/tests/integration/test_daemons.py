#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sh
import os


# Variables ===================================================================
DAEMONS = [
    "edeposit_amqp_alephdaemon.py",
    "edeposit_amqp_calibredaemon.py",
    "edeposit_amqp_ftp_managerd.py",
    "edeposit_amqp_ftp_monitord.py",
    "edeposit_amqp_tool.py"
]

CMD = {}
SH_CMD = {}


# Functions & objects =========================================================
def create_commands():
    global CMD
    global SH_CMD

    for daemon in DAEMONS:
        daemon_name = daemon.split("_", 2)[-1].split(".")[0]
        SH_CMD[daemon_name] = sh.Command("bin/%s" % daemon)
        CMD[daemon_name] = "bin/%s" % daemon


def test_daemon_existence():
    for daemon in DAEMONS:
        assert os.system("bin/%s -h" % daemon) == 0, daemon + " doesn't work!"

    create_commands()
