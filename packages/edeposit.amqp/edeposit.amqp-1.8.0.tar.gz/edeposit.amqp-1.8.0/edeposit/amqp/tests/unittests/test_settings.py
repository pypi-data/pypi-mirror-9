#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import settings


# Variables ===================================================================
STRINGS = [
    "RABBITMQ_HOST",
    "RABBITMQ_PORT",
    "RABBITMQ_USER_NAME",
    "RABBITMQ_USER_PASSWORD"
]


# Tests =======================================================================
def test_strings():
    for var in STRINGS:
        assert type(getattr(settings, var)) in [str, unicode]


def test_get_amqp_settings():
    assert settings.get_amqp_settings().keys() >= 3

    for key, val in settings.get_amqp_settings().items():
        assert "vhost" in val
        assert "exchange" in val
        assert "queues" in val
        assert "in_key" in val
        assert "out_key" in val
