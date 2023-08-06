#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
AMQP tool used for debugging and automatic RabbitMQ schema making.
"""
# Imports =====================================================================
import os
import sys
import json
import uuid
import os.path
import argparse
from functools import wraps


import pika

# if the module wasn't yet installed at this system, load it from package
try:
    import edeposit.amqp.settings as settings
    import edeposit.amqp.amqpdaemon as amqpdaemon
except ImportError:
    sys.path.insert(0, os.path.abspath('../edeposit/amqp'))

    import settings
    import amqpdaemon


# Functions & objects =========================================================
def test_virtualhost(fn):
    @wraps(fn)
    def catch_exception(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except pika.exceptions.ConnectionClosed:
            sys.stderr.write("Can't connect to virtuahost!\n")
            sys.stderr.write("Make sure, that virtualhost is created.\n")
            sys.exit()

    return catch_exception


@test_virtualhost
def create_blocking_connection(host):
    """
    Return properly created blocking connection.

    Args:
        host (str): Host as it is defined in :func:`.get_amqp_settings`.

    Uses :func:`edeposit.amqp.amqpdaemon.getConParams`.
    """
    return pika.BlockingConnection(
        amqpdaemon.getConParams(
            settings.get_amqp_settings()[host.lower()]["vhost"]
        )
    )


def create_schema(host):
    """
    Create exchanges, queues and route them.

    Args:
        host (str): One of the possible hosts.
    """
    connection = create_blocking_connection(host)
    channel = connection.channel()

    exchange = settings.get_amqp_settings()[host]["exchange"]
    channel.exchange_declare(
        exchange=exchange,
        exchange_type="topic",
        durable=True
    )
    print "Created exchange '%s'." % exchange
    print "Creating queues:"

    queues = settings.get_amqp_settings()[host]["queues"]
    for queue in queues.keys():
        channel.queue_declare(
            queue=queue,
            durable=True,
            # arguments={'x-message-ttl': int(1000 * 60 * 60 * 24)} # :S
        )
        print "\tCreated durable queue '%s'." % queue

    print
    print "Routing exchanges using routing key to queues:"

    for queue in queues.keys():
        channel.queue_bind(
            queue=queue,
            exchange=exchange,
            routing_key=queues[queue]
        )

        print "\tRouting exchange %s['%s'] -> '%s'." % (
            exchange,
            queues[queue],
            queue
        )


def _get_channel(host, timeout):
    """
    Create communication channel for given `host`.

    Args:
        host (str): Specified --host.
        timeout (int): Set `timeout` for returned `channel`.

    Returns:
        Object: Pika channel object.
    """
    connection = create_blocking_connection(host)

    # register timeout
    if timeout >= 0:
        connection.add_timeout(
            timeout,
            lambda: sys.stderr.write("Timeouted!\n") or sys.exit(1)
        )

    return connection.channel()


def receive(host, timeout):
    """
    Print all messages in queue.

    Args:
        host (str): Specified --host.
        timeout (int): How log should script wait for message.
    """
    parameters = settings.get_amqp_settings()[host]

    queues = parameters["queues"]
    queues = dict(map(lambda (x, y): (y, x), queues.items()))  # reverse items
    queue = queues[parameters["out_key"]]

    channel = _get_channel(host, timeout)
    for method_frame, properties, body in channel.consume(queue):
        print json.dumps({
            "method_frame": str(method_frame),
            "properties": str(properties),
            "body": body
        })
        print "-" * 79
        print

        channel.basic_ack(method_frame.delivery_tag)


def send_message(host, data, timeout=None, properties=None):
    """
    Send message to given `host`.

    Args:
        host (str): Specified host: aleph/ftp/whatever available host.
        data (str): JSON data.
        timeout (int, default None): How much time wait for connection.
    """
    channel = _get_channel(host, timeout)

    if not properties:
        properties = pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            headers={"UUID": str(uuid.uuid4())}
        )

    parameters = settings.get_amqp_settings()[host]

    channel.basic_publish(
        exchange=parameters["exchange"],
        routing_key=parameters["in_key"],
        properties=properties,
        body=data
    )


def get_list_of_hosts():
    """
    Returns:
        list: List of strings with names of possible hosts.
    """
    return settings.get_amqp_settings().keys()


def _require_host_parameter(args, to):
    """
    Make sure, that user specified --host argument.
    """
    if not args.host:
        sys.stderr.write("--host is required parameter to --%s\n" % to)
        sys.exit(1)


# Main program ================================================================
def main():
    # parse arguments
    parser = argparse.ArgumentParser(
        description="""AMQP tool used for debugging and automatic RabbitMQ
                       schema making."""
    )
    parser.add_argument(
        "-l",
        "--list",
        action='store_true',
        help="List all possible hosts."
    )
    parser.add_argument(
        "-s",
        "--host",
        choices=get_list_of_hosts() + ["all"],
        help="""Specify host. You can get list of valid host by using --list
                switch or use 'all' for all hosts."""
    )
    parser.add_argument(
        "-c",
        "--create",
        action='store_true',
        help="""Create exchanges/queues/routes for given host. --host is
                required."""
    )
    parser.add_argument(
        "-p",
        "--put",
        help="""Put message into input queue at given host. --put argument
                expects file with JSON data or - as indication of stdin data
                input."""
    )
    parser.add_argument(
        "-g",
        "--get",
        action='store_true',
        help="Get messages from --host output queue."
    )
    parser.add_argument(
        '-t',
        '--timeout',
        metavar="N",
        type=int,
        default=-1,
        help="Wait for message only N seconds."
    )
    args = parser.parse_args()

    if args.list:
        print "\n".join(get_list_of_hosts())
        sys.exit(0)

    if args.create:
        _require_host_parameter(args, "create")

        if args.host == "all":
            for host in get_list_of_hosts():
                create_schema(host)
        else:
            create_schema(args.host)

    if args.put:
        _require_host_parameter(args, "put")

        data = None
        if args.put == "-":
            data = sys.stdin.read()
        else:
            if not os.path.exists(args.put):
                sys.stderr.write("Can't open '%s'!\n" % args.put)
                sys.exit(1)

            with open(args.put) as f:
                data = f.read()

        send_message(args.host, data, args.timeout)

    if args.get:
        _require_host_parameter(args, "get")

        if args.host == "all":
            sys.stderr.write("Can't receive all hosts!\n")
            sys.exit(1)

        receive(args.host, args.timeout)


if __name__ == '__main__':
    try:
        main()
    except pika.exceptions.AMQPConnectionError:
        sys.stderr.write("Can't connect to RabbitMQ!\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print
        sys.exit(0)
