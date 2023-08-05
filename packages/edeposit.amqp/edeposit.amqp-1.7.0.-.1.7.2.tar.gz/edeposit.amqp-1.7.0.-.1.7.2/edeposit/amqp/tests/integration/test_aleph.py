#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import json

from aleph import *
import edeposit.amqp.serializers as serializers

from test_daemons import CMD, SH_CMD, create_commands


# Variables ===================================================================
ALEPH_TEST_OK = serializers.serialize(
    SearchRequest(ISBNQuery("80-251-0225-4"))
)


# Functions & objects =========================================================
def setup_module():
    create_commands()
    SH_CMD["alephdaemon"]("stop")

    # there are serious tty problems with sh module and DaemonWrapper, thats why
    os.system(CMD["alephdaemon"] + " start")


def parse_data(data):
    spacer = "-" * 79
    out = data.split(spacer)[-2]
    out = json.loads(out)["body"]
    return serializers.deserialize(out, globals())

def send_and_return(host, data):
    tool = SH_CMD["tool"]
    tool(put="-", host=host, _in=data)

    return tool(get=True, host=host, timeout="2", _ok_code=[1])


def test_good():
    # send request to alephW
    out = send_and_return("aleph", ALEPH_TEST_OK)

    # check request
    data = parse_data(out)

    assert len(data.records) > 0
    assert data.records[0].base == "nkc"
    assert data.records[0].epublication.ISBN == ['80-251-0225-4']


def test_bad():
    out = send_and_return("aleph", "asd")
    # data = parse_data(out)

    assert "No JSON object could be decoded" in out
    assert "ValueError" in out


def teardown_module(module):
    SH_CMD["alephdaemon"]("stop")
