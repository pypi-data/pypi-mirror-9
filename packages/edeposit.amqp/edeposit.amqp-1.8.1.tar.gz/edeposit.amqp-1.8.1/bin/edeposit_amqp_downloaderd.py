#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
"""
AMQP binding for downloader workers. See `edeposit.amqp.downloader
<https://github.com/edeposit/edeposit.amqp.downloader>`_ for details.
"""
import os
import sys
import os.path
import argparse


from pika.exceptions import ConnectionClosed

from edeposit.amqp.downloader import *
from edeposit.amqp.downloader.structures import *


# if the amqp module wasn't yet installed at this system, load it from package
try:
    from edeposit.amqp import settings
except ImportError:
    sys.path.insert(0, os.path.abspath('../edeposit/'))
    import amqp
    sys.modules["edeposit.amqp"] = amqp


from edeposit.amqp.amqpdaemon import AMQPDaemon, getConParams
from edeposit.amqp import settings


# Functions & objects =========================================================
def main(args, stop=False):
    """
    Arguments parsing, etc..
    """
    daemon = AMQPDaemon(
        con_param=getConParams(
            settings.RABBITMQ_DOWNER_VIRTUALHOST
        ),
        queue=settings.RABBITMQ_DOWNER_INPUT_QUEUE,
        out_exch=settings.RABBITMQ_DOWNER_EXCHANGE,
        out_key=settings.RABBITMQ_DOWNER_OUTPUT_KEY,
        react_fn=reactToAMQPMessage,
        glob=globals()                # used in deserializer
    )

    if not stop and args.foreground:  # run at foreground
        daemon.run()
    else:
        daemon.run_daemon()           # run as daemon


# Main program ================================================================
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        main(None, stop=True)
        sys.exit(0)

    parser = argparse.ArgumentParser(
        usage='%(prog)s start/stop/restart [-f/--foreground]',
        description="""AMQP binding for downloader."""
    )
    parser.add_argument(
        "action",
        metavar="start/stop/restart",
        type=str,
        default=None,
        help="Start/stop/restart the daemon."
    )
    parser.add_argument(
        "-f",
        '--foreground',
        action="store_true",
        required=False,
        help="""Run at foreground, not as daemon. If not set, script is will
                run at background as unix daemon."""
    )
    args = parser.parse_args()

    try:
        main(args)
    except ConnectionClosed as e:
        sys.stderr.write(
            e.message + " - is the RabbitMQ queues properly set?\n"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        pass
