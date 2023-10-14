-- Script to load vocabulary tables from 'athena.ohdsi.org' in CSV
-- format into an SQLite DB.
--
-- First create the tables by running:
--     sqlite3 <vocab-db-file> < tables_vocab.sqlite.sql
-- Optionally create indexes by following with:
--     sqlite3 <vocab-db-file> < indexes_vocab.sqlite.sql
-- You may also want to follow either of the previous commands with:
--     sqlite3 <vocab-db-file> vacuum

-- Copyright (c) 2023 Aubrey Barnard.
--
-- This is free software released under the MIT License.  See
-- `LICENSE.txt` for details.


-- Increase memory bounds (probably doesn't help much for loading)
pragma mmap_size=536870912; -- 0.5 GiB in B
pragma cache_size=-524288; -- 0.5 GiB in KiB

-- Setup for "raw" tab-separated values.  This accommodates concept
-- names that contain unquoted occurrences of double quotes (of which
-- there are many).
.mode ascii
.separator "\t" "\n"
-- See 'https://sqlite.org/cli.html#importing_files_as_csv_or_other_formats'
-- for details.  (By default '.import' assumes CSV according to RFC
-- 4180, 'https://datatracker.ietf.org/doc/html/rfc4180'.)

-- All the files have a 1-line header
.import --skip 1 CONCEPT.csv concept
.import --skip 1 CONCEPT_ANCESTOR.csv concept_ancestor
.import --skip 1 CONCEPT_CLASS.csv concept_class
.import --skip 1 CONCEPT_RELATIONSHIP.csv concept_relationship
.import --skip 1 CONCEPT_SYNONYM.csv concept_synonym
.import --skip 1 DOMAIN.csv domain
.import --skip 1 DRUG_STRENGTH.csv drug_strength
.import --skip 1 RELATIONSHIP.csv relationship
.import --skip 1 VOCABULARY.csv vocabulary

-- Load the CPT4 concepts which I placed in a separate file.  If you ran
-- 'cpt.sh' as instructed so that 'CONCEPT.csv' already includes the
-- CPT4 concepts, then this is not needed.
--.import CONCEPT.CPT4.csv concept

-- Report the numbers of rows loaded
select count(*) as 'n rows concept:' from concept;
-- n rows concept:
-- 6312604  -- = 6295989 + 16615
select count(*) as 'n rows concept_ancestor:' from concept_ancestor;
-- n rows concept_ancestor:
-- 76495949
select count(*) as 'n rows concept_class:' from concept_class;
-- n rows concept_class:
-- 415
select count(*) as 'n rows concept_relationship:' from concept_relationship;
-- n rows concept_relationship:
-- 50192848
select count(*) as 'n rows concept_synonym:' from concept_synonym;
-- n rows concept_synonym:
-- 2624705
select count(*) as 'n rows domain:' from domain;
-- n rows domain:
-- 48
select count(*) as 'n rows drug_strength:' from drug_strength;
-- n rows drug_strength:
-- 2936415
select count(*) as 'n rows relationship:' from relationship;
-- n rows relationship:
-- 672
select count(*) as 'n rows vocabulary:' from vocabulary;
-- n rows vocabulary:
-- 75
