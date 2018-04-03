SQLite DBs
==========


This directory contains SQLite databases that make our clean tabular
(CSV) data available for querying with SQL tools or language DB APIs.
There are DBs for the versions of the MCRF OMOP CDM data, the CDM
vocabulary, and examples for various classification tasks.

The DBs can be used for interactive querying by running `sqlite3
<db-name>`.  Note that you will have to attach
(https://sqlite.org/lang_attach.html) the other DBs if you want to work
with more than one at once.  You can also use any programming language
library or other SQL tools that you prefer.

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

All the dates are in "%Y-%m-%d" format so that they are automatically
compatible with SQLite's date functions
(https://sqlite.org/lang_datefunc.html), Unix core utilities, and
typical programming language libraries.


-----

Copyright (c) 2018 Aubrey Barnard.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.
