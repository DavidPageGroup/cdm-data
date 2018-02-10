-- Definition of tables to hold CDM clinical data, SQLite3 syntax, CDM
-- version 5.1?

-- Copyright (c) 2018 DPRG CDM Data.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.

-- See http://sqlite.org/lang_createtable.html on syntax for creating
-- tables and http://sqlite.org/datatype3.html for information on
-- SQLite3 data types

-- See https://github.com/OHDSI/CommonDataModel and
-- https://github.com/OHDSI/CommonDataModel/wiki for information on the
-- CDM

-- Omit column constraints (e.g. not null) because data is messy

create table person (
    person_id int,
    gender_concept_id int,
    year_of_birth int,
    month_of_birth int,
    day_of_birth int,
    time_of_birth text,
    race_concept_id int,
    ethnicity_concept_id int,
    location_id int,
    provider_id int,
    care_site_id int,
    person_source_value text,
    gender_source_value text,
    gender_source_concept_id int,
    race_source_value text,
    race_source_concept_id int,
    ethnicity_source_value text,
    ethnicity_source_concept_id int
);

create table condition_occurrence (
    condition_occurrence_id int,
    person_id int,
    condition_concept_id int,
    condition_start_date text,
    condition_end_date text,
    condition_type_concept_id int,
    stop_reason text,
    provider_id int,
    visit_occurrence_id int,
    condition_source_value text,
    condition_source_concept_id int
);

create table drug_exposure (
    drug_exposure_id int,
    person_id int,
    drug_concept_id int,
    drug_exposure_start_date text,
    drug_exposure_end_date text,
    drug_type_concept_id int,
    stop_reason text,
    refills int,
    quantity real,
    days_supply int,
    sig text,
    route_concept_id int,
    effective_drug_dose real,
    dose_unit_concept_id int,
    lot_number text,
    provider_id int,
    visit_occurrence_id int,
    drug_source_value text,
    drug_source_concept_id int,
    route_source_value text,
    dose_unit_source_value text
);

create table measurement (
    measurement_id int,
    person_id int,
    measurement_concept_id int,
    measurement_date text,
    measurement_time text,
    measurement_type_concept_id int,
    operator_concept_id int,
    value_as_number num,
    value_as_concept_id int,
    unit_concept_id int,
    range_low num,
    range_high num,
    provider_id int,
    visit_occurrence_id int,
    measurement_source_value text,
    measurement_source_concept_id int,
    unit_source_value text,
    value_source_value text
);

create table procedure_occurrence (
    procedure_occurrence_id int,
    person_id int,
    procedure_concept_id int,
    procedure_date text,
    procedure_type_concept_id int,
    modifier_concept_id int,
    quantity int,
    provider_id int,
    visit_occurrence_id int,
    procedure_source_value text,
    procedure_source_concept_id int,
    qualifier_source_value text
);

create table visit_occurrence (
    visit_occurrence_id int,
    person_id int,
    visit_concept_id int,
    visit_start_date text,
    visit_start_time text,
    visit_end_date text,
    visit_end_time text,
    visit_type_concept_id int,
    provider_id int,
    care_site_id int,
    visit_source_value text,
    visit_source_concept_id int
);
