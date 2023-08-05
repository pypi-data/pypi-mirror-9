#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Filenames are generated dynamically. Here is set of constructors for those
filanames.
"""
# Imports =====================================================================
import os.path


# Functions & objects =========================================================
def _get_suffix(path):
    """
    Return suffix from `path`.

    ``/home/xex/somefile.txt`` --> ``txt``.

    Args:
        path (str): Full file path.

    Returns:
        str: Suffix.

    Raises:
        UserWarning: When ``/`` is detected in suffix.
    """
    suffix = os.path.basename(path).split(".")[-1]

    if "/" in suffix:
        raise UserWarning("Filename can't contain '/' in suffix (%s)!" % path)

    return suffix


def original_fn(book_id, ebook_fn):
    """
    Construct original filename from `book_id` and `ebook_fn`.

    Args:
        book_id (int/str): ID of the book, without special characters.
        ebook_fn (str): Original name of the ebook. Used to get suffix.

    Returns:
        str: Filename in format ``oc_nk-BOOKID.suffix``.
    """
    return "oc_" + str(book_id) + "." + _get_suffix(ebook_fn)


def metadata_fn(book_id):
    """
    Construct filename for metadata file.

    Args:
        book_id (int/str): ID of the book, without special characters.

    Returns:
        str: Filename in format ``meds_nk-BOOKID.xml``.
    """
    return "mods_" + str(book_id) + ".xml"


def volume_fn(cnt):
    """
    Construct filename for 'volume' metadata file.

    Args:
        cnt (int): Number of the MODS record.

    Returns:
        str: Filename in format ``mods_volume.xml`` or ``mods_volume_cnt.xml``.
    """
    return "mods_volume%s.xml" % ("_%d" if cnt > 0 else "")


def checksum_fn(book_id):
    """
    Construct filename for checksum file.

    Args:
        book_id (int/str): ID of the book, without special characters.

    Returns:
        str: Filename in format ``MD5_BOOKID.md5``.
    """
    return "MD5_" + str(book_id) + ".md5"


def info_fn(book_id):
    """
    Construct filename for info.xml file.

    Args:
        book_id (int/str): ID of the book, without special characters.

    Returns:
        str: Filename in format ``info_BOOKID.xml``.
    """
    return "info_" + str(book_id) + ".xml"
