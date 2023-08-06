#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from structures.requests import RST2PDF
from structures.requests import GenerateReview
from structures.requests import GenerateContract

from structures.responses import pdf_from_file

from translator import gen_pdf
from specialization import get_review
from specialization import get_contract


# Functions & classes =========================================================
def _instanceof(instance, class_):
    """Check type by matching ``.__name__``."""
    return type(instance).__name__ == class_.__name__


def reactToAMQPMessage(message, sender):
    """
    React to given (AMQP) message. `message` is usually expected to be
    :py:func:`collections.namedtuple` structure filled with all necessary data.

    Args:
        message (\*Request class): One of the structures defined in
                :mod:`.requests`.
        sender (fn reference): Reference to function for responding - progress
               monitoring for example. Function takes one parameter, which
               may be response namedtuple, or string or whatever would be
               normally returned.

    Returns:
        obj: One of the responses in :mod:`.responses`.

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    if _instanceof(message, GenerateContract):
        return pdf_from_file(  # TODO: rewrite to decorator
            get_contract(**message._asdict())
        )
    elif _instanceof(message, RST2PDF):
        return pdf_from_file(
            gen_pdf(**message._asdict())
        )
    elif _instanceof(message, GenerateReview):
        return pdf_from_file(
            get_review(message)
        )

    raise ValueError(
        "Unknown type of request: '" + str(type(message)) + "'!"
    )
