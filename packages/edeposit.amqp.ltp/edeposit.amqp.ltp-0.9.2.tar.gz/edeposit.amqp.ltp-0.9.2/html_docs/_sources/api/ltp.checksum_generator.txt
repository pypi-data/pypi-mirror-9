checksum_generator submodule
============================

This submodule is used to generate MD5 checksums for data and metadata files in
SIP package.

It also used to create `hash file`, which holds all checksums with paths
to the files from root of the package. For example path
``/home/xex/packageroot/somedir/somefile.txt`` will be stored as
``/packageroot/somedir/somefile.txt``.

API
---

.. automodule:: ltp.checksum_generator
    :members:
    :undoc-members:
    :show-inheritance:
    :private-members:
