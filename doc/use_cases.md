Use Cases for the CDM-Format Data
=================================


Here are the use cases for the data that have been mentioned so far.  I
have ranked them roughly by popularity of use.

* data exploration
  * data types
  * range of values
  * summary statistics
  * GUI, web UI for exploring / visualizing data
* draw subsets / batches
  * to support a specific study
  * random sample (e.g. for testing)
  * batches for SGD or similar for deep learning
* query patient timelines
  * assemble patient timelines
* query events
  * support phenotype definition
  * support data trimming
* create feature vectors from relational data
  * feature functions in SQL
* make / use [OHDSI method]( https://www.ohdsi.org/methods-library/)
  * need relational DBMS with CDM-format data
* assemble dataset from Condor job (?)
* remapping IDs for deidentification / compression (?)


-----

Copyright (c) 2018 Aubrey Barnard.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.
