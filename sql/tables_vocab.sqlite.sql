-- Definition of tables to hold CDM vocabulary data.  See the
-- accompanying definition of clinical tables for more information.

-- Copyright (c) 2018 DPRG CDM Data.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.

create table concept (
    concept_id int,
    concept_name text,
    domain_id text,
    vocabulary_id text,
    concept_class_id text,
    standard_concept text,
    concept_code text,
    valid_start_date text,
    valid_end_date text,
    invalid_reason text
);

create table concept_ancestor (
    ancestor_concept_id int,
    descendant_concept_id int,
    min_levels_of_separation int,
    max_levels_of_separation int
);

create table concept_class (
    concept_class_id text,
    concept_class_name text,
    concept_class_concept_id int
);

create table concept_relationship (
    concept_id_1 int,
    concept_id_2 int,
    relationship_id int,
    valid_start_date text,
    valid_end_date text,
    invalid_reason text
);

create table concept_synonym (
    concept_id int,
    concept_synonym_name text,
    language_concept_id int
);

create table domain (
    domain_id text,
    domain_name text,
    domain_concept_id int
);

create table drug_strength (
    drug_concept_id int,
    ingredient_concept_id int,
    amount_value num,
    amount_unit_concept_id int,
    numerator_value num,
    numerator_unit_concept_id int,
    denominator_value num,
    denominator_unit_concept_id int,
    box_size int,
    valid_start_date text,
    valid_end_date text,
    invalid_reason text
);

create table relationship (
    relationship_id text,
    relationship_name text,
    is_hierarchical text,
    defines_ancestry text,
    reverse_relationship_id text,
    relationship_concept_id int
);

create table vocabulary (
    vocabulary_id text,
    vocabulary_name text,
    vocabulary_reference text,
    vocabulary_version text,
    vocabulary_concept_id int
);
