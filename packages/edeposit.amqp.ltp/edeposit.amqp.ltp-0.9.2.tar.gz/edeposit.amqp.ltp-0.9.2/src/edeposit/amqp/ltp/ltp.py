#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import uuid
import time
import shutil
import base64
import os.path
import hashlib
from collections import OrderedDict

import xmltodict
from edeposit.amqp.aleph import marcxml

import settings

import fn_composers
import checksum_generator
from xslt_transformer import transform_to_mods
from mods_postprocessor import _remove_hairs


# Functions & objects =========================================================
def _get_package_name(prefix=settings.TEMP_DIR):
    """
    Return package path. Use uuid to generate package's directory name.

    Args:
        prefix (str): Where the package will be stored. Default
                      :attr:`settings.TEMP_DIR`.

    Returns:
        str: Path to the root directory.
    """
    return os.path.join(
        prefix,
        str(uuid.uuid4())
    )


def _create_package_hierarchy(prefix=settings.TEMP_DIR):
    """
    Create hierarchy of directories, at it is required in specification.

    `root_dir` is root of the package generated using :attr:`settings.TEMP_DIR`
    and :func:`_get_package_name`.

    `orig_dir` is path to the directory, where the data files are stored.

    `metadata_dir` is path to the directory with MODS metadata.

    Args:
        prefix (str): Path to the directory where the `root_dir` will be
                      stored.

    Warning:
        If the `root_dir` exists, it is REMOVED!

    Returns:
        list of str: root_dir, orig_dir, metadata_dir
    """
    root_dir = _get_package_name(prefix)

    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)

    os.mkdir(root_dir)

    original_dir = os.path.join(root_dir, "original")
    metadata_dir = os.path.join(root_dir, "metadata")

    os.mkdir(original_dir)
    os.mkdir(metadata_dir)

    return root_dir, original_dir, metadata_dir


def _get_localized_fn(path, root_dir):
    """
    Return absolute `path` relative to `root_dir`.

    When `path` == ``/home/xex/somefile.txt`` and `root_dir` == ``/home``,
    returned path will be ``/xex/somefile.txt``.

    Args:
        path (str): Absolute path beginning in `root_dir`.
        root_dir (str): Absolute path containing `path` argument.

    Returns:
        str: Local `path` when `root_dir` is considered as root of FS.
    """
    local_fn = path
    if path.startswith(root_dir):
        local_fn = path.replace(root_dir, "", 1)

    if not local_fn.startswith("/"):
        return "/" + local_fn

    return local_fn


def _path_to_id(path):
    """
    Name of the root directory is used as ``<packageid>`` in ``info.xml``.

    This function makes sure, that :func:`os.path.basename` doesn't return
    blank string in case that there is `/` at the end of the `path`.

    Args:
        path (str): Path to the root directory.

    Returns:
        str: Basename of the `path`.
    """
    if path.endswith("/"):
        path = path[:-1]

    return os.path.basename(path)


def _calc_dir_size(path):
    """
    Calculate size of all files in `path`.

    Args:
        path (str): Path to the directory.

    Returns:
        int: Size of the directory in bytes.
    """
    dir_size = 0
    for (root, dirs, files) in os.walk(path):
        for fn in files:
            full_fn = os.path.join(root, fn)
            dir_size += os.path.getsize(full_fn)

    return dir_size


def _add_order(inp_dict):
    """
    Add order to unordered dict.

    Order is taken from *priority table*, which is just something I did to
    make outputs from `xmltodict` look like examples in specification.

    Args:
        inp_dict (dict): Unordered dictionary.

    Returns:
        OrderedDict: Dictionary ordered by *priority table*.
    """
    out = OrderedDict()

    priority_table = [
        "created",
        "metadataversion",
        "packageid",
        "mainmets",
        "titleid",
        "collection",
        "institution",
        "creator",
        "size",
        "itemlist",
        "checksum"
    ]
    priority_table = dict(  # construct dict keys -> {key: order}
        map(
            lambda (cnt, key): (key, cnt),
            enumerate(priority_table)
        )
    )

    sorted_keys = sorted(
        inp_dict.keys(),
        key=lambda x: priority_table.get(x, x)
    )
    for key in sorted_keys:
        out[key] = inp_dict[key]

    return out


def _compose_info(root_dir, files, hash_fn, aleph_record):
    """
    Compose `info` XML file.

    Info example::

        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <info>
            <created>2014-07-31T10:58:53</created>
            <metadataversion>1.0</metadataversion>
            <packageid>c88f5a50-7b34-11e2-b930-005056827e51</packageid>
            <mainmets>mets.xml</mainmets>
            <titleid type="ccnb">cnb001852189</titleid>
            <titleid type="isbn">978-80-85979-89-6</titleid>
            <collection>edeposit</collection>
            <institution>nakladatelství Altar</institution>
            <creator>ABA001</creator>
            <size>1530226</size>
            <itemlist itemtotal="1">
                <item>\data\Denik_zajatce_Sramek_CZ_v30f-font.epub</item>
            </itemlist>
            <checksum type="MD5" checksum="ce076548eaade33888005de5d4634a0d">
                \MD5.md5
            </checksum>
        </info>

    Args:
        root_dir (str): Absolute path to the root directory.
        original_fn (str): Absolute path to the ebook file.
        metadata_fn (str): Absolute path to the metadata file.
        hash_fn (str): Absolute path to the MD5 file.
        aleph_record (str): String with Aleph record with metadata.

    Returns:
        str: XML string.
    """
    # compute hash for hashfile
    with open(hash_fn) as f:
        hash_file_md5 = hashlib.md5(f.read()).hexdigest()

    document = {
        "info": {
            "created": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "metadataversion": "1.0",
            "packageid": _path_to_id(root_dir),

            # not used in SIP
            # "mainmets": _get_localized_fn(metadata_fn, root_dir),

            "itemlist": {
                "@itemtotal": "2",
                "item": map(
                    lambda x: _get_localized_fn(x, root_dir),
                    files
                )
            },
            "checksum": {
                "@type": "MD5",
                "@checksum": hash_file_md5,
                "#text": _get_localized_fn(hash_fn, root_dir)
            },
            "collection": "edeposit",
            "size": _calc_dir_size(root_dir) / 1024,  # size in kiB
        }
    }

    # get informations from MARC record
    record = marcxml.MARCXMLRecord(aleph_record)

    # get publisher info
    if record.getPublisher(None):
        document["info"]["institution"] = _remove_hairs(
            record.getPublisher()
        )

    # get <creator> info
    creator = record.getDataRecords("910", "a", False)
    alt_creator = record.getDataRecords("040", "d", False)
    document["info"]["creator"] = creator[0] if creator else alt_creator[-1]

    # collect informations for <titleid> tags
    isbns = record.getISBNs()

    ccnb = record.getDataRecords("015", "a", False)
    ccnb = ccnb[0] if ccnb else None

    if any([isbns, ccnb]):  # TODO: issn
        document["info"]["titleid"] = []

    for isbn in isbns:
        document["info"]["titleid"].append({
            "@type": "isbn",
            "#text": isbn
        })

    if ccnb:
        document["info"]["titleid"].append({
            "@type": "ccnb",
            "#text": ccnb
        })

    # TODO: later
    # if issn:
    #     document["info"]["titleid"].append({
    #         "@type": "issn",
    #         "#text": issn
    #     })

    document["info"] = _add_order(document["info"])
    xml_document = xmltodict.unparse(document, pretty=True)

    # return xml_document.replace("<?xml ", '<?xml standalone="yes" ')
    return xml_document


def create_ltp_package(aleph_record, book_id, ebook_fn, b64_data):
    """
    Create LTP package as it is specified in specification v1.0 as I understand
    it.

    Args:
        aleph_record (str): XML containing full aleph record.
        book_id (int): More or less unique ID of the book.
        ebook_fn (str): Original filename of the ebook.
        b64_data (str): Ebook file encoded in base64 string.

    Returns:
        str: Name of the package's directory in ``/tmp``.
    """
    root_dir, orig_dir, meta_dir = _create_package_hierarchy()

    book_id = _path_to_id(root_dir)

    # create original file
    original_fn = os.path.join(
        orig_dir,
        fn_composers.original_fn(book_id, ebook_fn)
    )
    with open(original_fn, "wb") as f:
        f.write(
            base64.b64decode(b64_data)
        )

    # create metadata files
    metadata_filenames = []
    records = transform_to_mods(aleph_record, book_id)
    for cnt, mods_record in enumerate(records):
        fn = os.path.join(
            meta_dir,
            fn_composers.volume_fn(cnt)
        )

        with open(fn, "w") as f:
            f.write(mods_record)

        metadata_filenames.append(fn)

    # collect md5 sums
    md5_fn = os.path.join(root_dir, fn_composers.checksum_fn(book_id))
    checksums = checksum_generator.generate_hashfile(root_dir)
    with open(md5_fn, "w") as f:
        f.write(checksums)

    # create info file
    info_fn = os.path.join(root_dir, fn_composers.info_fn(book_id))
    with open(info_fn, "w") as f:
        f.write(
            _compose_info(
                root_dir=root_dir,
                files=[original_fn] + metadata_filenames,
                hash_fn=md5_fn,
                aleph_record=aleph_record,
            )
        )

    return root_dir
