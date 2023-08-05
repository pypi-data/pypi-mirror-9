#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from base64 import b64encode

# requests
from structures.requests import Download
from structures.requests import ProgressDownload
from structures.requests import CheckExistence

# responses
from structures.responses import DownloadedFile
from structures.responses import Progress
from structures.responses import Exists

import downloader


# Functions & classes =========================================================
def get_progress_reporter(send_back):
    """
    Construct progress reporter callback from `send_back` function.

    Args:
        send_back (fn reference): Reference to function for sending messages
                  back using AMQP.

    Returns:
        fn reference: Function taking 3 parameters as is required by \
                      :func:`.progress_download`.
    """
    def progress_reporter_callback(step, downloaded, content_len):
        send_back(
            Progress(
                step=step,
                downloaded=downloaded,
                content_length=content_len
            )
        )

    return progress_reporter_callback


def _instanceof(instance, class_):
    """Check type by matching ``.__name__``."""
    return type(instance).__name__ == class_.__name__


def reactToAMQPMessage(message, send_back):
    """
    React to given (AMQP) message. `message` is usually expected to be
    :py:func:`collections.namedtuple` structure filled with all necessary data.

    Args:
        message (\*Request class): only :class:`.ConversionRequest` class is
                                   supported right now
        send_back (fn reference): Reference to function for responding. This is
                  useful for progress monitoring for example. Function takes
                  one parameter, which may be response structure/namedtuple, or
                  string or whatever would be normally returned.

    Returns:
        ConversionResponse: response filled with data about conversion and\
                            converted file.

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    if _instanceof(message, Download):
        return DownloadedFile(
            url=message.url,
            b64_data=b64encode(
                downloader.download(message.url)
            )
        )
    elif _instanceof(message, CheckExistence):
        exists = True

        # not nice, but you would not believe, how many exceptions are there to
        # throw
        try:
            headers = downloader.head_request(message.url)
        except Exception:
            exists = False
            headers = {}

        return Exists(
            url=message.url,
            result=exists,
            headers=headers
        )
    elif _instanceof(message, ProgressDownload):
        return DownloadedFile(
            url=message.url,
            b64_data=b64encode(
                downloader.progress_download(
                    url=message.url,
                    steps=message.steps,
                    callback=get_progress_reporter(send_back)
                )
            )
        )

    raise ValueError(
        "Unknown type of request: '" + str(type(message)) + "'!"
    )
