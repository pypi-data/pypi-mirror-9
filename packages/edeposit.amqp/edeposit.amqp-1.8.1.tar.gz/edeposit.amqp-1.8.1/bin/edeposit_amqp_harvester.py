#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
AMQP interface for edeposit.amqp.harvester
(https://github.com/edeposit/edeposit.amqp.harvester/)
"""
# Imports =====================================================================
import sys
import uuid
import argparse
import traceback

import pika

from edeposit_amqp_tool import send_message

import edeposit.amqp.harvester as harvester
from harvester.structures import Publications


# Functions & objects =========================================================
def _process_exception(e, body, tb):
    """
    Process informations about exception and send them thru AMQP.

    Args:
        e (obj): Exception instance.
        body (str): Text which will be sent over AMQP.
        tb (obj): Traceback object with informations, which will be put to the
                  headers.
    """
    # get informations about message
    msg = e.message if hasattr(e, "message") else str(e)
    exception_type = str(e.__class__)
    exception_name = str(e.__class__.__name__)

    properties = pika.BasicProperties(
        content_type="application/text",
        delivery_mode=2,
        headers={
            "exception": msg,
            "exception_type": exception_type,
            "exception_name": exception_name,
            "traceback": tb,
            "UUID": str(uuid.uuid4())
        }
    )

    send_message("harvester", body, properties=properties)


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""This script is used to send data from
                       edeposit.amqp.harvester to AMQP queue."""
    )
    parser.add_argument(
        "-u",
        "--unittest",
        action="store_true",
        help="Perform unittest."
    )
    parser.add_argument(
        "-r",
        "--harvest",
        action="store_true",
        help="Harvest all data and send them to harvester queue."
    )
    args = parser.parse_args()

    if args.unittest:
        try:
            harvester.self_test()
        except Exception, e:
            _process_exception(e, str(e), traceback.format_exc().strip())
            sys.exit(1)
    elif args.harvest:
        send_message(
            "harvester",
            Publications(harvester.get_all_publications())
        )
    else:
        parser.print_help()
