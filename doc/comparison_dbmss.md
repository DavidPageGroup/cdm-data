Comparison of Database Management Systems (DBMSs)
=================================================


Ad Hoc / No DBMS
----------------

This is the current state of affairs where we each write the processing
we need to do on the data without any help from a data processing
engine.

Examples:
* CSV library for your language (e.g. Python `csv`)
* table library for your language (e.g. R dataframe)
* Unix command line utilities (coreutils) like `grep` and `cut`
* csvkit

Pros:
* language library
  * accessible, no need to learn DBMSs
  * integrates well with surrounding code
* coreutils
  * fast
  * easily can be parallel

Cons:
* language library
  * have to write own data processing
    * error-prone
    * inefficient
  * typically require data to fit in RAM
* coreutils
  * do not understand data format -> fallible
  * can only do a single, simple query at a time (must use shell to glue together)
* tend to be slow (no indexes, no parallelism, no distributed processing)

csvkit bridges the ad hoc and embedded approaches.  It is basically a
set of command line utilities that understand tabular / delimited data
and so has characteristics of both coreutils and CSV libraries.


Embedded
--------

An embedded database is essentially a (relational) data processing
engine available as a library (API).  That is, it runs in the same
process as the application and does not have a client-server
architecture.

Examples:
* SQLite
* MonetDBLite

Pros:
* minimal / no setup
  * no DB server / administration
* scalable (each user executes their own processing)

Cons:
* often lacks functionality present in common RDBMSs
  * no access controls beyond filesystem
  * limited concurrency
* queries can be slow because execution is not distributed and might not
  be parallel
* library not always available for your language


RDBMS
-----

When people talk about a database, this is often what they mean: a
relational database that stores data in tables, can be queried with SQL,
and runs with a client-server architecture.  Some RDBMSs support query
processing in parallel or distributing data and processing across a
cluster of computers.

Examples:
* MySQL / MariaDB
* PostgreSQL
* Oracle
* MonetDB (column store)

Pros:
* "enterprise" features
  * high concurrency
  * hot backup
  * access control
* taught in school
* standard query API (ODBC)
  * declarative query language

Cons:
* needs dedicated server
* requires lots of setup / administration
* learning curve
* often cumbersome query API not idiomatic to host language
* $


NoSQL
-----

This is the catch-all bucket of other, fairly recent database
technologies and encompasses many different types of DBMSs
(https://en.wikipedia.org/wiki/NoSQL).  The main characteristics are
that data is not necessarily stored in tables (non-relational) and
interaction is via an API, not a query language like SQL ("no SQL",
although some do support SQL or some other query language).

Examples:
https://en.wikipedia.org/wiki/NoSQL#Types_and_examples_of_NoSQL_databases

Pros:
* fast, distributed query execution
* scalability (scale out data and processing)

Cons:
* needs cluster
* requires lots of setup / administration
* learning curve
* query functionality can be limited, must be supplemented in host
  language (write own code to process data)
* $$$
