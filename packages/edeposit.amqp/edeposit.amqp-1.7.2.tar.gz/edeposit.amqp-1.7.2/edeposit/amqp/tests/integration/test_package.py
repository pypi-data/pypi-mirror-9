#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import urllib


# Tests =======================================================================
def test_pypi_package():
    package_name = "edeposit.amqp"
    url = "https://pypi.python.org/pypi/%s/" % package_name

    f = urllib.urlopen(url)
    assert f.getcode() == 200


def test_pip_package():
    assert os.system("pip search edeposit.amqp") == 0
