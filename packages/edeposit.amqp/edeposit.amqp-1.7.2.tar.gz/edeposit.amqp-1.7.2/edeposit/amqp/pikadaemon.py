#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
Generic AMQP blocking communication daemon server.

Usage is simple - just inherit the class and override
:func:`PikaDaemon.onMessageReceived`.

You can send messages back using either :func:`PikaDaemon.sendMessage` or
:func:`PikaDaemon.sendResponse`. Fist one allows you to send message
everywhere, second one send message to the queue defined by constructor.
"""
import pika


import daemonwrapper


#= Functions & objects ========================================================
class PikaDaemon(daemonwrapper.DaemonRunnerWrapper):
    def __init__(self, connection_param, queue, output_exchange, output_key):
        """
        Pika and Daemon wrapper for handling AMQP connections.

        Args:
            connection_param (pika.ConnectionParameters): object setting the
                             connection
            queue (str): name of queue where the daemon should listen
            output_exchange (str): name of exchange where the daemon should put
                                   responses
            output_key (str): routing key for output exchange
        """
        super(PikaDaemon, self).__init__(queue)

        self.connection_param = connection_param

        self.queue = queue
        self.output_exchange = output_exchange

        self.content_type = "application/json"

        self.output_key = output_key

        self.ack_sent = False
        self.ack_delivery_tag = None

    def body(self):
        """
        This method just handles AMQP connection details and receive loop.

        Warning:
            Don't override this method!
        """
        self.connection = pika.BlockingConnection(self.connection_param)
        self.channel = self.connection.channel()

        # receive messages and put them to .onMessageReceived() callback
        for method_frame, properties, body in self.channel.consume(self.queue):
            self.ack_sent = False
            self.ack_delivery_tag = method_frame.delivery_tag
            if self.onMessageReceived(method_frame, properties, body):
                self.ack()

    def ack(self):
        """
        Acknowledge, that message was received.

        Note:
            This will in some cases (depends on settings of RabbitMQ) remove
            the message from the message queue.
        """
        if not self.ack_sent:
            self.channel.basic_ack(self.ack_delivery_tag)
            self.ack_sent = True

    def onMessageReceived(self, method_frame, properties, body):
        """
        Callback which is called every time when message is received.

        Warning:
            You SHOULD override this.

        Note:
            It is expected, that method returns True, if you want to
            automatically ack the received message, which can be important in
            some situations, because otherwise the message will be held in
            message queue until someone will ack it.

            You don't have to return True/False - you can ack the message
            yourself, by calling :func:`ack`.

        Note:
            Good design choice is to ack the message AFTER you process it, to
            be sure, that message is processed properly and can be removed from
            queue.
        """
        print "method_frame:", method_frame
        print "properties:", properties
        print "body:", body

        print "---"
        print

    def sendMessage(self, exchange, routing_key, message, properties=None,
                    UUID=None):
        """
        With this function, you can send message to `exchange`.

        Args:
            exchange (str): name of exchange you want to message to be
                            delivered
            routing_key (str): which routing key to use in headers of message
            message (str): body of message
            properties (dict ,optional): properties of message - if not used,
                                      or set to ``None``, ``self.content_type``
                                      and ``delivery_mode=2`` (persistent) is
                                      used
            UUID (str, optional): UUID of the message. If set, it is included
                                  into ``properties`` of the message.
        """
        if properties is None:
            properties = pika.BasicProperties(
                content_type=self.content_type,
                delivery_mode=1,
                headers={}
            )

        if UUID is not None:
            if properties.headers is None:
                properties.headers = {}
            properties.headers["UUID"] = UUID

        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            properties=properties,
            body=message
        )

    def sendResponse(self, message, UUID, routing_key):
        """
        Send `message` to ``self.output_exchange`` with routing key
        ``self.output_key``, ``self.content_type`` in ``delivery_mode=2``.

        Args:
            message (str): message which will be sent
            UUID: unique identification of message
            routing_key (str): which routing key to use to send message back
        """
        self.sendMessage(
            exchange=self.output_exchange,
            routing_key=routing_key,
            message=message,
            UUID=UUID
        )

    def onExit(self):
        """
        Called when daemon is stopped. Basically just AMQP's ``.close()``
        functions to ensure clean exit.

        You can override this, but don't forget to call it thru ``super()``, or
        the AMQP communication won't be closed properly!
        """
        def try_call(fn):
            try:
                fn()
            except (pika.exceptions.ChannelClosed, AttributeError,
                    pika.exceptions.ConnectionClosed):
                return

        if hasattr(self, "channel"):
            try_call(self.channel.cancel)
            try_call(self.channel.close)
            try_call(self.connection.close)
