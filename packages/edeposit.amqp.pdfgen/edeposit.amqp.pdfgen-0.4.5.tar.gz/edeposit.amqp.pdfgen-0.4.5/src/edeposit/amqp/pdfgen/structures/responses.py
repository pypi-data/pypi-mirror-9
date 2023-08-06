#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from base64 import b64encode
from collections import namedtuple


# Functions & classes =========================================================
def pdf_from_file(file_obj):
    """
    Convert `file_obj` to base64 string.

    Args:
        file_obj (obj): Opened file like object.

    Returns:
        str: Base64 encoded string.
    """
    return PDF(
        b64encode(file_obj.read())
    )


class PDF(namedtuple("PDF", ["b64_content"])):
    """
    Response to request containing base64 representation of genrated PDF.

    Attributes:
        b64_content (str): Base64 string.
    """
    pass
