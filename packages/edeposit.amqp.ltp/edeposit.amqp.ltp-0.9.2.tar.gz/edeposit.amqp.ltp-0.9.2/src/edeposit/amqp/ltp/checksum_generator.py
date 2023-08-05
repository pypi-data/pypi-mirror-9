#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Checksum generator in format specified in LTP specification.
"""
# Imports =====================================================================
import os
import hashlib


# Variables ===================================================================
_BLACKLIST = {
    "info.xml"
}


# Functions & objects =========================================================
def _get_required_fn(fn, root_path):
    """
    Definition of the MD5 file requires, that all paths will be absolute
    for the package directory, not for the filesystem.

    This function converts filesystem-absolute paths to package-absolute paths.

    Args:
        fn (str): Local/absolute path to the file.
        root_path (str): Local/absolute path to the package directory.

    Returns:
        str: Package-absolute path to the file.

    Raises:
        ValueError: When `fn` is absolute and `root_path` relative or \
                    conversely.
    """
    if not fn.startswith(root_path):
        raise ValueError("Both paths have to be absolute or local!")

    replacer = "/" if root_path.endswith("/") else ""

    return fn.replace(root_path, replacer, 1)


def generate_checksums(directory, blacklist=_BLACKLIST):
    """
    Compute checksum for each file in `directory`, with exception of files
    specified in `blacklist`.

    Args:
        directory (str): Absolute or relative path to the directory.
        blacklist (list/set/tuple): List of blacklisted filenames. Only
                  filenames are checked, not paths!

    Returns:
        dict: Dict in format ``{fn: md5_hash}``.

    Note:
        File paths are returned as absolute paths from package root.

    Raises:
        UserWarning: When `directory` doesn't exists.
    """
    if not os.path.exists(directory):
        raise UserWarning("'%s' doesn't exists!" % directory)

    hashes = {}
    for root, dirs, files in os.walk(directory):
        for fn in sorted(files):
            # skip files on blacklist
            if fn in blacklist:
                continue

            fn = os.path.join(root, fn)

            # compute hash of the file
            with open(fn) as f:
                checksum = hashlib.md5(f.read())

            fn = _get_required_fn(fn, directory)

            hashes[fn] = checksum.hexdigest()

    return hashes


def generate_hashfile(directory, blacklist=_BLACKLIST):
    """
    Compute checksum for each file in `directory`, with exception of files
    specified in `blacklist`.

    Args:
        directory (str): Absolute or relative path to the directory.
        blacklist (list/set/tuple): List of blacklisted filenames. Only
                  filenames are checked, not paths!

    Returns:
        str: Content of hashfile as it is specified in ABNF specification for \
             project.
    """
    checksums = generate_checksums(directory, blacklist)

    out = ""
    for fn, checksum in sorted(checksums.items()):
        out += "%s %s\n" % (checksum, fn)

    return out
