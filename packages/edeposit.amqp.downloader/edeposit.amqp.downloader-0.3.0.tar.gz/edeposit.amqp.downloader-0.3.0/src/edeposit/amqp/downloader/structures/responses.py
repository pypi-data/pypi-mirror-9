#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple


# Functions & classes =========================================================
class DownloadedFile(namedtuple("DownloadedFile", ["url", "b64_data"])):
    """
    Response to :class:`.Download` and :class:`.ProgressDownload`.

    Attributes:
        url (str): URL of the internet resource.
        b64_data (str): Downloaded data encoded as base64 string.
    """
    pass


class Progress(namedtuple("Progress", ["url", "step", "downloaded",
                                                      "content_length"])):
    """
    Response to :class:`.ProgressDownload`.

    Attributes:
        url (str): URL of the internet resource.
        step (int): Number of current step.
        downloaded (int): How many bytes was downloaded to this step.
        content_length (int): How big is the whole file (in bytes).
    """
    pass


class Exists(namedtuple("Exists", ["url", "result", "headers"])):
    """
    Response to :class:`.CheckExistence`.

    Attributes:
        url (str): URL of the internet resource.
        result (bool): ``True`` if the file exists, ``False`` if not.
        headers (dict): HTTP headers returned to this requests.
    """
    pass
