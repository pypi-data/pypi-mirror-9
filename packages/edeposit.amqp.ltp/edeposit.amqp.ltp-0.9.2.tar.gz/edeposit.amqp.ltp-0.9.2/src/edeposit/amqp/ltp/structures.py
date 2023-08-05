#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from collections import namedtuple


# Communication classes =======================================================
class ExportRequest(namedtuple("ExportRequest", ["aleph_record",
                                                 "book_uuid",
                                                 "filename",
                                                 "b64_data"])):
    """
    Request structure holding data to export to LTP.

    Attributes:
        aleph_record (str): String with complete MARC XML / OAI MARC record.
        book_uuid (str): Unique ID of the book. This have to be in UUID4
                         format!
        filename (str): Original filename name of the epublication.
        b64_data (str): Epublication serialized as BASE64 data string.
    """
    pass


class TrackingRequest(namedtuple("TrackingRequest", ["book_uuid"])):
    """
    Ask for state of the export request.

    Attributes:
        book_uuid (str): UUID of the book you want to track.
    """
    pass


class TrackingState():
    def __init__(self, exported, error):
        self.exported = exported
        self.error = error


class TrackingResult():
    def __init__(self, book_id, state):
        self.book_id = book_id
        self.state = state
