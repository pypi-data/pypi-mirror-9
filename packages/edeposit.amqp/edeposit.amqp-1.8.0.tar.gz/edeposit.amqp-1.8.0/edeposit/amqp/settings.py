#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module is containing all necessary global variables for package.

Module also has ability to read user-defined data from two paths:
$HOME/:attr:`SETTINGS_PATH` and /etc/:attr:`SETTINGS_PATH`.

Note:
    If the first path is found, other is ignored.

Example of the configuration file (``$HOME/edeposit/amqp.json``)::

    {
        "RABBITMQ_HOST": "localhost",
        "RABBITMQ_PORT": "2222"
    }

Attributes
----------
"""
import json
import os
import os.path


#= module configuration =======================================================
RABBITMQ_HOST = '127.0.0.1'  #:
RABBITMQ_PORT = '5672'  #:
RABBITMQ_USER_NAME = 'guest'  #:
RABBITMQ_USER_PASSWORD = 'guest'  #:

# aleph's settings
RABBITMQ_ALEPH_VIRTUALHOST = "aleph"   #:
RABBITMQ_ALEPH_INPUT_QUEUE = "daemon"  #:
RABBITMQ_ALEPH_OUTPUT_QUEUE = "plone"  #:
RABBITMQ_ALEPH_EXCHANGE = "search"     #:

RABBITMQ_ALEPH_INPUT_KEY = "request"   #:
RABBITMQ_ALEPH_OUTPUT_KEY = "result"   #:
RABBITMQ_ALEPH_EXCEPTION_KEY = "exception"  #:

# calibre's settings
RABBITMQ_CALIBRE_VIRTUALHOST = "calibre"  #:
RABBITMQ_CALIBRE_INPUT_QUEUE = "daemon"   #:
RABBITMQ_CALIBRE_OUTPUT_QUEUE = "plone"   #:
RABBITMQ_CALIBRE_EXCHANGE = "convert"     #:

RABBITMQ_CALIBRE_INPUT_KEY = "request"  #:
RABBITMQ_CALIBRE_OUTPUT_KEY = "result"  #:

# settings for edeposit.amqp.ftp daemon
RABBITMQ_FTP_VIRTUALHOST = "ftp"     #: Virtualhost for FTP module
RABBITMQ_FTP_INPUT_QUEUE = "daemon"  #: Input Queue for FTP AMQP daemon
RABBITMQ_FTP_OUTPUT_QUEUE = "plone"  #: Queue to put responses from daemon
RABBITMQ_FTP_EXCHANGE = "ftp"

RABBITMQ_FTP_INPUT_KEY = "request"  #:
RABBITMQ_FTP_OUTPUT_KEY = "result"  #:

# settings for edeposit.amqp.antivirus daemon
RABBITMQ_ANTIVIRUS_VIRTUALHOST = "antivirus"  #: Virtualhost for AV module
RABBITMQ_ANTIVIRUS_INPUT_QUEUE = "daemon"     #: Input Queue for AV AMQP daemon
RABBITMQ_ANTIVIRUS_OUTPUT_QUEUE = "plone"     #: Queue to put responses
RABBITMQ_ANTIVIRUS_EXCHANGE = "antivirus"

RABBITMQ_ANTIVIRUS_INPUT_KEY = "request"  #:
RABBITMQ_ANTIVIRUS_OUTPUT_KEY = "result"  #:

# settings for edeposit.amqp.harvester
RABBITMQ_HARVESTER_VIRTUALHOST = "harvester"  #: Virtualhost for harvester
RABBITMQ_HARVESTER_INPUT_QUEUE = "daemon"     #: Input Queue for harvester
RABBITMQ_HARVESTER_OUTPUT_QUEUE = "plone"     #: Queue to put responses
RABBITMQ_HARVESTER_EXCHANGE = "harvester"

RABBITMQ_HARVESTER_INPUT_KEY = "request"  #:
RABBITMQ_HARVESTER_OUTPUT_KEY = "result"  #:

# settings for edeposit.amqp.ltp
RABBITMQ_LTP_VIRTUALHOST = "ltp"     #: Virtualhost for ltp
RABBITMQ_LTP_INPUT_QUEUE = "daemon"  #: Input Queue for ltp
RABBITMQ_LTP_OUTPUT_QUEUE = "plone"  #: Queue to put responses
RABBITMQ_LTP_EXCHANGE = "ltp"

RABBITMQ_LTP_INPUT_KEY = "request"  #:
RABBITMQ_LTP_OUTPUT_KEY = "result"  #:


# settings for edeposit.amqp.pdfgen
RABBITMQ_PDFGEN_VIRTUALHOST = "pdfgen"  #: Virtualhost for pdfgen
RABBITMQ_PDFGEN_INPUT_QUEUE = "daemon"  #: Input Queue for pdfgen
RABBITMQ_PDFGEN_OUTPUT_QUEUE = "plone"  #: Queue to put responses
RABBITMQ_PDFGEN_EXCHANGE = "pdfgen"

RABBITMQ_PDFGEN_INPUT_KEY = "request"  #:
RABBITMQ_PDFGEN_OUTPUT_KEY = "result"  #:


# settings for edeposit.amqp.downloader
RABBITMQ_DOWNER_VIRTUALHOST = "downloader"  #: Virtualhost for downloader
RABBITMQ_DOWNER_INPUT_QUEUE = "daemon"  #: Input Queue for downloader
RABBITMQ_DOWNER_OUTPUT_QUEUE = "plone"  #: Queue to put responses
RABBITMQ_DOWNER_EXCHANGE = "downloader"

RABBITMQ_DOWNER_INPUT_KEY = "request"  #:
RABBITMQ_DOWNER_OUTPUT_KEY = "result"  #:


def get_amqp_settings():
    """
    Return all settings in dict in following format::

        {
            "submodule_name": {
                "vhost": VIRTUALHOST,
                "exchange": EXCHANGE,
                "queues": {
                    QUEUE_NAME: ROUTING_KEY,
                    QUEUE_NAME: ROUTING_KEY
                },
                "in_key": INPUT_KEY,
                "out_key": OUTPUT_KEY
            },
            ...
        }
    """
    amqp_settings = {}
    for vhost in filter(lambda x: x.endswith("VIRTUALHOST"), globals().keys()):
        vhost = "RABBITMQ_" + vhost.split("_")[1]

        queues = {
            globals()[vhost + "_INPUT_QUEUE"]: globals()[vhost + "_INPUT_KEY"],
            globals()[vhost + "_OUTPUT_QUEUE"]: globals()[vhost + "_OUTPUT_KEY"]
        }

        amqp_settings[vhost.split("_")[-1].lower()] = {
            "vhost": globals()[vhost + "_VIRTUALHOST"],
            "exchange": globals()[vhost + "_EXCHANGE"],
            "queues": queues,
            "in_key": globals()[vhost + "_INPUT_KEY"],
            "out_key": globals()[vhost + "_OUTPUT_KEY"]
        }

    return amqp_settings


#= user configuration reader ==================================================
_ALLOWED = [unicode, str, int, float]

SETTINGS_PATH = "/edeposit/amqp.json"
"""
Path which is appended to default search paths (``$HOME`` and ``/etc``).

Note:
    It has to start with ``/``. Variable is **appended** to the default search
    paths, so this doesn't mean, that the path is absolute!
"""


def get_all_constants():
    """
    Get list of all uppercase, non-private globals (doesn't start with ``_``).

    Returns:
        list: Uppercase names defined in `globals()` (variables from this \
              module).
    """
    return filter(
        lambda key: key.upper() == key and type(globals()[key]) in _ALLOWED,

        filter(                               # filter _PRIVATE variables
            lambda x: not x.startswith("_"),
            globals().keys()
        )
    )


def substitute_globals(config_dict):
    """
    Set global variables to values defined in `config_dict`.

    Args:
        config_dict (dict): dictionary with data, which are used to set \
                            `globals`.

    Note:
        `config_dict` have to be dictionary, or it is ignored. Also all
        variables, that are not already in globals, or are not types defined in
        :attr:`_ALLOWED` (str, int, float) or starts with ``_`` are silently
        ignored.
    """
    constants = get_all_constants()

    if type(config_dict) != dict:
        return

    for key in config_dict.keys():
        if key in constants and type(config_dict[key]) in _ALLOWED:
            globals()[key] = config_dict[key]


# try to read data from configuration paths ($HOME/SETTINGS_PATH,
# /etc/SETTINGS_PATH)
if "HOME" in os.environ and os.path.exists(os.environ["HOME"] + SETTINGS_PATH):
    with open(os.environ["HOME"] + SETTINGS_PATH) as f:
        substitute_globals(json.loads(f.read()))
elif os.path.exists("/etc" + SETTINGS_PATH):
    with open("/etc" + SETTINGS_PATH) as f:
        substitute_globals(json.loads(f.read()))
