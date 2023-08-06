Banner Ad Toolkit
=================

Author: Tim Santor tsantor@xstudios.agency
------------------------------------------

Overview
========

A couple of command line helpers to (1) auto-generate blank PSDs at
specific sizes with desired filenames and (2) automatically save static
image versions without going over predefined max file sizes. Very useful
for people who design and develop a lot of banner ad campaigns.

Requirements
============

-  Python 2.7.x
-  ImageMagick
-  pngquant

NOTE: This has only been tested on a Mac (10.10.2) at this time.

Installation
============

You can install directly via pip:

::

    pip install Banner-Ad-Toolkit

Or from the BitBucket repository (master branch by default):

::

    git clone https://bitbucket.org/tsantor/banner-ad-toolkit
    cd banner-ad-toolkit
    sudo python setup.py install

Usage
=====

Create a Manifest
-----------------

Both command line tools are governed by a manifest file. Create an Excel
doc with the following column headers and add as many rows as needed for
each banner size you need:

+----------+---------+----------+------------+---------------------+---------------------+
| Type     | Width   | Height   | Max Size   | Prefix              | Suffix              |
+==========+=========+==========+============+=====================+=====================+
| Static   | 300     | 600      | 40KB       | PREFIX (optional)   | SUFFIX (optional)   |
+----------+---------+----------+------------+---------------------+---------------------+
| Static   | 160     | 600      | 40KB       | PREFIX (optional)   | SUFFIX (optional)   |
+----------+---------+----------+------------+---------------------+---------------------+
| Static   | 300     | 250      | 40KB       | PREFIX (optional)   | SUFFIX (optional)   |
+----------+---------+----------+------------+---------------------+---------------------+
| Static   | 728     | 90       | 40KB       | PREFIX (optional)   | SUFFIX (optional)   |
+----------+---------+----------+------------+---------------------+---------------------+

NOTE: Columns may be in any order. You may add any additional columns you need,
but they will be ignored.

-  **Type:** ``Static``, ``Flash`` or anything else, however Flash types
   will be ignored (currently) by the tools.
-  **Max Size:** File size should be defined using KB or MB (eg -
   ``40KB``, ``1MB``)
-  **Prefix:** A prefix to prepend to your file name
-  **Suffix:** A suffix to append to your file name

NOTE: File names will be generated as ``PREFIX_WIDTHxHEIGHT_SUFFIX``

Export as CSV
-------------

Export (Save As) your Excel doc as a CSV.

Generate PSDs
-------------

Once you have your manifest CSV, we can auto-generate blank PSDs at
specific sizes with desired filenames. Simply run the following command:

::

    adkit-generate /path/to/manifest.csv /path/to/output

NOTE: For all available commands, run ``adkit-generate -h``

Export Deliverables
-------------------

Once all your banner PSDs are complete, ensure they are saved in their
'static' state. This will automatically save static image versions
without going over predefined max file sizes defined in the manifest.
Simply run the following command:

::

    adkit-export /path/to/manifest.csv /path/to/input/ /path/to/output

NOTE: For all available commands, run ``adkit-export -h``

Issues
------

If you experience any issues, please create an
`issue <https://bitbucket.org/tsantor/banner-ad-toolkit/issues>`__ on
Bitbucket.
