Simple PYTHON file distribution library.
========================================

Description:
----------------------------------------

Simple library that allows organize distribution of files within hex based tree.

Install FileDistribution package:
----------------------------------------

.. code-block:: console

    $ pip install FileDistribution

Example of usage:
----------------------------------------

.. code-block:: python

    from file_distribution import FileDistribution

    fd = FileDistribution("/tmp/storage")

    # default extensions
    database_id = 1
    fd.hex_path(database_id)
    fd.rename_from("/tmp/upload/file1.txt")
    path = fd.get_path() # saved file path

    # set all extensions to .pdf
    database_id = 256
    fd.set_extension(".pdf")
    fd.hex_path(database_id)
    fd.rename_from("/tmp/upload/file2.txt")
    path = fd.get_path() # saved file path

Files should be stored in /tmp/storage/01.dat and /tmp/storage/01/00.pdf