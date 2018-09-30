-- Definition of tables to hold CDM clinical data, SQLite3 syntax, CDM
-- version 5.1?

-- Copyright (c) 2018 Aubrey Barnard.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.

-- See http://sqlite.org/lang_createtable.html on syntax for creating
-- tables and http://sqlite.org/datatype3.html for information on
-- SQLite3 data types

-- See https://github.com/OHDSI/CommonDataModel and
-- https://github.com/OHDSI/CommonDataModel/wiki for information on the
-- CDM

-- Omit column constraints (e.g. not null) because data is messy


-- Clinical data tables
-- (alphabetical except `person` first)

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
    condition_start_datetime text,
    condition_end_date text,
    condition_end_datetime text,
    condition_type_concept_id int,
    stop_reason text,
    provider_id int,
    visit_occurrence_id int,
    condition_source_value text,
    condition_source_concept_id int,
    condition_status_source_value text,
    condition_status_concept_id int
);

create table death (
    person_id int,
    death_date text,
    death_datetime text,
    death_type_concept_id int,
    cause_concept_id int,
    cause_source_value text,
    cause_source_concept_id int
);

create table drug_exposure (
    drug_exposure_id int,
    person_id int,
    drug_concept_id int,
    drug_exposure_start_date text,
    drug_exposure_start_datetime text,
    drug_exposure_end_date text,
    drug_exposure_end_datetime text,
    verbatim_end_date text,
    drug_type_concept_id int,
    stop_reason text,
    refills int,
    quantity real,
    days_supply int,
    sig text,
    route_concept_id int,
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
    measurement_datetime text,
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

create table observation (
    observation_id int,
    person_id int,
    observation_concept_id int,
    observation_date text,
    observation_datetime text,
    observation_type_concept_id int,
    value_as_number num,
    value_as_string text,
    value_as_concept_id int,
    qualifier_concept_id int,
    unit_concept_id int,
    provider_id int,
    visit_occurrence_id int,
    observation_source_value text,
    observation_source_concept_id int,
    unit_source_value text,
    qualifier_source_value text
);

create table procedure_occurrence (
    procedure_occurrence_id int,
    person_id int,
    procedure_concept_id int,
    procedure_date text,
    procedure_datetime text,
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
    visit_start_datetime text,
    visit_end_date text,
    visit_end_datetime text,
    visit_type_concept_id int,
    provider_id int,
    care_site_id int,
    admitting_source_concept_id int,
    discharge_to_concept_id int,
    preceding_visit_occurrence_id int,
    visit_source_value text,
    visit_source_concept_id int,
    admitting_source_value text,
    discharge_to_source_value text
);


-- Health system data tables

create table care_site (
    care_site_id int,
    care_site_name text,
    place_of_service_concept_id int,
    location_id int,
    care_site_source_value text,
    place_of_service_source_value text
);

create table location (
    location_id int,
    address_1 text,
    address_2 text,
    city text,
    state text,
    zip text,
    county text,
    location_source_value text
);
