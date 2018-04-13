About this Directory and its Data
=================================


Cooperation
-----------

This volume is large but finite.  Please use it wisely and sparingly,
especially for things that do not benefit others.  Doing so will help
ensure that everybody is able to work with the data and that multiple
versions of the data can be maintained as we get updates.  For example,
you can store temporary / working data in `/scratch`, `/ua/ml-group`, or
`/z/Comp/page`.  Just make sure to protect it with strict permissions
(`chmod -R go-rwx`).  Compressing your data will also help.

You can communicate with others working on this data by using our
Office365 group.  Ask me if I haven't already made you a member.

If you would like to contribute content (documentation, programs, etc.),
use our GitHub repository: https://github.com/DavidPageGroup/cdm-data.
You can either make a pull request, ask for write access to the
repository, or send me (small) updates by e-mail.

The more we can cooperate the easier we will find working with this
data.

(By the way, if you want to see who has access to the data, the members
of our Unix group, run `getent group | grep mcrf`.)


Data
----

The "raw" CDM-format data is contained in the directories named
`omop_data.*`.  Since there are multiple versions of the data, the
directories are tagged with the extraction date and any comment.  You
probably want to work with the clean data rather than the raw data.


Cleaned, Sorted, and Compressed Data
------------------------------------

I have cleaned, sorted, and compressed each version of the "raw" data
into a corresponding `clean_data.*` directory.  On a shared network
filesystem such as ours, the compressed data can be faster to access in
many cases.  See `clean_data.*` and `clean_data.*/CONTENTS.md` in
particular for more information.


File Formats
------------

The formats of the files found here are described in
`clean_data.*/CONTENTS.md` and in `tables.yaml`.


OMOP / CDM / Athena Vocabulary
------------------------------

The "vocabulary" (the names and concepts) needed to understand the codes
in this data have been provided in the `vocab` directory.  Information
about the vocabulary files can be found at
https://github.com/OHDSI/CommonDataModel/wiki.  The vocabulary contents
can be browsed online at http://athena.ohdsi.org/, and there is some
background information at https://www.ohdsi.org/analytic-tools/.


SQLite DBs
----------

The cleaned data, vocabulary, and examples are also available in
relational database form in the directory `sqlite_dbs`.  The DB format
is SQLite 3 (https://sqlite.org/).


Contact
-------

If you have any questions, send e-mail to me (Aubrey) or our Office365
group.


-----

Copyright (c) 2018 Aubrey Barnard.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.
