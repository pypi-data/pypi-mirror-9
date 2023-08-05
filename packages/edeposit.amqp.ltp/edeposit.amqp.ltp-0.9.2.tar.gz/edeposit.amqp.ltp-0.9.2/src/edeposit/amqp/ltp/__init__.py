#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import shutil
import os.path

import ltp
import settings
import structures


# Functions & objects =========================================================
def _instanceof(instance, cls):
    """
    Check type of `instance` by matching ``.__name__`` with `cls.__name__`.
    """
    return type(instance).__name__ == cls.__name__


# Main program ================================================================
def reactToAMQPMessage(message, send_back):
    """
    React to given (AMQP) message. `message` is expected to be
    :py:func:`collections.namedtuple` structure from :mod:`.structures` filled
    with all necessary data.

    Args:
        message (object): One of the request objects defined in
                          :mod:`.structures`.
        send_back (fn reference): Reference to function for responding. This is
                  useful for progress monitoring for example. Function takes
                  one parameter, which may be response structure/namedtuple, or
                  string or whatever would be normally returned.

    Returns:
        object: Response class from :mod:`.structures`.

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    if _instanceof(message, structures.ExportRequest):
        tmp_folder = ltp.create_ltp_package(
            aleph_record=message.aleph_record,
            book_id=message.book_uuid,
            ebook_fn=message.filename,
            b64_data=message.b64_data
        )

        out_dir = os.path.join(settings.EXPORT_DIR, tmp_folder)
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        shutil.move(tmp_folder, settings.EXPORT_DIR)
        # return structures.ScanResult(message.filename, result)

    raise ValueError(
        "Unknown type of request: '" + str(type(message)) + "'!"
    )
