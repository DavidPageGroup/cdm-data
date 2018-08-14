SQLite DBs
==========


This directory contains SQLite databases that make our clean tabular
(CSV) data available for querying with SQL tools or language DB APIs.
There are DBs for the versions of the MCRF OMOP CDM data, the CDM
vocabulary, and examples for various classification tasks.

### naming convention

The emr DBs are named following the convention 
'db_name.date_of_download.additional_info.sqlite3' where db_name is
one of 'mcrf', 'emr', 'vocab', date_of_download (YYYYMMDD) indicates the date
MCRF csv files were downloaded, and additional_info is used to provide addional
information about the contents of the DB file.  Users wishing to share
derived database files are encouraged to follow this format.

### queries

The DBs can be used for interactive querying by running `sqlite3
<db-name>`.  Note that you will have to attach
(https://sqlite.org/lang_attach.html) the other DBs if you want to work
with more than one at once.  You can also use any programming language
library or other SQL tools that you prefer.

### indexes
 
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

### date fields
All the dates are in "%Y-%m-%d" format so that they are automatically
compatible with SQLite's date functions
(https://sqlite.org/lang_datefunc.html), Unix core utilities, and
typical programming language libraries.


-----

Copyright (c) 2018 Aubrey Barnard, Jon Badger.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.
