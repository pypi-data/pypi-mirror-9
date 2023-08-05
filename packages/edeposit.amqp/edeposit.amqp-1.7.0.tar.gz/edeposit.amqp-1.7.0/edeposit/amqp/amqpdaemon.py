#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
"""
This module provides generic AMQP daemon and builder of common connection
informations, which are defined as constants in :mod:`edeposit.amqp.settings`.

Daemon is used by :mod:`edeposit_amqp_alephdaemon` and
:mod:`edeposit_amqp_calibredaemon`.
"""
import traceback

import pika

try:
    import serializers
except ImportError:
    import edeposit.amqp.serializers as serializers

import pikadaemon
import settings


#= Functions & objects ========================================================
def getConParams(virtualhost):
    """
    Connection object builder.

    Args:
        virtualhost (str): selected virtualhost in rabbitmq

    Returns:
        pika.ConnectionParameters: object filled by `constants` from
        :class:`edeposit.amqp.settings`.
    """
    return pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=int(settings.RABBITMQ_PORT),
        virtual_host=virtualhost,
        credentials=pika.PlainCredentials(
            settings.RABBITMQ_USER_NAME,
            settings.RABBITMQ_USER_PASSWORD
        )
    )


class AMQPDaemon(pikadaemon.PikaDaemon):
    def __init__(self, con_param, queue, out_exch, out_key, react_fn, glob):
        """
        Args:
            con_param (ConnectionParameters): see :func:`getConParams` for
                                              details
            queue (str):    name of the queue
            out_exch (str): name of the exchange for outgoing messages
            out_key (str):  what key will be used to send messages back
            react_fn (fn):  function, which can react to messages, see Note for
                            details
            glob (dict):    result of ``globals()`` call - used in deserializer
                            to automatically build classes, which are not
                            available in this namespace of this package

        Note:
            ``react_fn`` parameter is expected to be function, which gets two
            parameters - `message` (some form of message, it can be also
            namedtuple), and `UUID` containing unique identificator of the
            message.

        Example of function used as `react_fn` parameter::

            def reactToAMQPMessage(message, UUID):
                response = None
                if message == 1:
                    return 2
                elif message == "Hello":
                    return "Hi"
                elif type(message) == dict:
                    return {1: 2}

                raise UserWarning("Unrecognized message")

        As you can see, protocol is pretty easy. You get `message`, to which you
        react somehow and return `response`. Thats all.
        """
        super(AMQPDaemon, self).__init__(
            con_param, queue, out_exch, out_key
        )

        self.react_fn = react_fn
        self.globals = glob

    def parseKey(self, method_frame):
        key = ""
        if hasattr(method_frame, "routing_key"):
            key = method_frame.routing_key

        if "." in key:
            key = key.rsplit(".", 1)[0] + "." + self.output_key
        else:
            key = self.output_key

        return key

    def onMessageReceived(self, method_frame, properties, body):
        """
        React to received message - deserialize it, add it to users reaction
        function stored in ``self.react_fn`` and send back result.

        If `Exception` is thrown during process, it is sent back instead of
        message.

        Note:
            In case of `Exception`, response message doesn't have useful `body`,
            but in headers is stored following (string) parameters:

            - ``exception``, where the Exception's message is stored
            - ``exception_type``, where ``e.__class__`` is stored
            - ``exception_name``, where ``e.__class__.__name__`` is stored
            - ``traceback`` where the full traceback is stored (contains line
              number)

            This allows you to react to unexpected cases at the other end of
            the AMQP communication.
        """
        # if UUID is not in headers, just ack the message and ignore it
        if "UUID" not in properties.headers:
            self.process_exception(
                e=ValueError("No UUID provided, message ignored."),
                uuid="",
                routing_key=self.parseKey(method_frame),
                body=body
            )
            return True  # ack message

        uuid = properties.headers["UUID"]
        try:
            result = self.react_fn(
                serializers.deserialize(body, self.globals),
                uuid
            )
            print "sending response", self.parseKey(method_frame)
            self.sendResponse(
                serializers.serialize(result),
                uuid,
                self.parseKey(method_frame)
            )
        except Exception, e:
            self.process_exception(
                e,
                uuid,
                self.parseKey(method_frame),
                str(e),
                tb=traceback.format_exc().strip()
            )

        return True  # ack message

    def process_exception(self, e, uuid, routing_key, body, tb=None):
        # get informations about message
        msg = e.message if hasattr(e, "message") else str(e)
        exception_type = str(e.__class__)
        exception_name = str(e.__class__.__name__)

        self.sendMessage(
            self.output_exchange,
            routing_key,
            str(body),
            properties=pika.BasicProperties(
                content_type="application/text",
                delivery_mode=2,
                headers={
                    "exception": msg,
                    "exception_type": exception_type,
                    "exception_name": exception_name,
                    "traceback": tb,
                    "UUID": uuid
                }
            )
        )
