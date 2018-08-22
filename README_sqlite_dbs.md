SQLite DBs
==========


This directory contains SQLite databases that make our clean tabular
(CSV) data available for querying with SQL tools or language DB APIs.
There are DBs for the versions of the MCRF OMOP CDM data, the CDM
vocabulary, and examples for various classification tasks.


Queries
-------

The DBs can be used for interactive querying by running `sqlite3
<db-name>`.  Note that you will have to attach
(https://sqlite.org/lang_attach.html) the other DBs if you want to work
with more than one at once.  You can also use any programming language
library or other SQL tools that you prefer.


Indexes
-------

The DBs have indexes on the columns that can be used for lookup.  Let me
know if you think your queries could benefit from other indexes.  Note
that SQLite does not have indexes that will help with searching for
keywords.  Thus, there is no way to speed up searching for concept
descriptions, for example.  (Running `grep <keyword> vocab/concept.csv`
may be faster and meet your accuracy needs.)  Also, note that the DB
engine may decide to use a table scan instead of an index lookup in some
cases, like where most of the table needs to be scanned anyway.  Thus,
more indexes don't always help performance and such performance issues
need to be analyzed on a case-by-case basis (see
https://sqlite.org/lang_explain.html).


Date fields
-----------

All the dates are in "%Y-%m-%d" format so that they are automatically
compatible with SQLite's date functions
(https://sqlite.org/lang_datefunc.html), Unix core utilities, and
typical programming language libraries.


DB naming convention
-----------------

The EMR DBs are named following the convention <db_name> "." <data_date>
("."<tags\>)? ".sqlite3" where db_name is one of 'mcrf', 'emr', 'vocab',
data_date (YYYYMMDD) indicates the version of MCRF data based on
download date, and tags is an extensible field separated with dashes.
(ex ...<data_date>.<tag-tag>.sqlite3) that can be used to provide
additional information about the contents of the DB file.  Users wishing
to share derived database files are encouraged to follow this format to
assist with data version tracking and searchability.


-----

Copyright (c) 2018 Aubrey Barnard, Jon Badger.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.
