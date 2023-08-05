#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple


# Functions & classes =========================================================
class Download(namedtuple("Download", ["url"])):
    """
    Download data from `url`.

    Attributes:
        url (str): URL of the internet resource.

    Returns:
        obj: :class:`.DownloadedFile`.
    """
    pass


class ProgressDownload(namedtuple("ProgressDownload", ["url", "steps"])):
    """
    Download data from `url` and report back the progress.

    Attributes:
        url (str): URL of the internet resource.
        steps (int): Number of steps used to track progress.

    Progress is reported using :class:`.Progress` structure.

    Returns:
        obj: :class:`.DownloadedFile`.
    """
    pass


class CheckExistence(namedtuple("CheckExistence", ["url"])):
    """
    Send HEAD request to given `url` and check it's existence.

    Attributes:
        url (str): URL of the internet resource.

    Returns:
        obj: :class:`.Exists`.
    """
    pass
