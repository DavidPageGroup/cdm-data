-- Extracts and outputs events and facts from CDM data.  Bringing the
-- data together in this way allows one to easily query event sequences
-- and thus patient histories.  A fact is just like an event except that
-- it doesn't have any temporal information attached.

-- Copyright (c) 2018 Aubrey Barnard.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.

-- Requires SQLite >= 3.9, which introduced JSON support.  Download the
-- latest SQLite from https://www.sqlite.org/download.html.  Or, if you
-- need 64-bit support, build it yourself:
-- https://www.sqlite.org/howtocompile.html.

-- For information on using JSON in SQLite, see
-- https://www.sqlite.org/json1.html.

-- See `dump_events.sqlite.sh` for an example of how to run.

-- Each row will be losslessly encoded as an event by extracting event
-- attributes that will live in the event table and then storing the
-- remainder of the row as JSON.  (Meaningless values are excluded to
-- save space.  See individual comments.)

-- Start
.shell date +'%FT%T emr_to_events.sqlite.sql: Starting to generate events' >&2

-- Log configuration.  Set number of threads.
.output stderr
pragma mmap_size;
pragma cache_size;
pragma temp_store;
pragma threads = 4;
.output stdout

-- Generate biographic / demographic facts.  Facts have to be done one
-- type at a time so that the column name can be used as the event type.
-- To save space, don't include JSON with the facts, but include the
-- original record as an additional fact.

-- Date of birth
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading date of birth from `person`' >&2
select person_id, null, null,
       -- DOB was put in `time_of_birth`
       'bx', 'dob', time_of_birth, null
from person
where person_id is not null
  and time_of_birth is not null
--limit 10 -- when testing
;

-- Gender
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading gender from `person`' >&2
select person_id, null, null,
       -- Use character code (F,M,U) instead of concept ID
       'bx', 'gndr', gender_source_value, null
from person
where person_id is not null
  and gender_source_value is not null
--limit 10 -- when testing
;

-- Race
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading race from `person`' >&2
select person_id, null, null,
       'bx', 'race', race_concept_id, null
from person
where person_id is not null
  and race_concept_id is not null
--limit 10 -- when testing
;

-- Ethnicity
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading ethnicity from `person`' >&2
select person_id, null, null,
       'bx', 'ethn', ethnicity_concept_id, null
from person
where person_id is not null
  and ethnicity_concept_id is not null
--limit 10 -- when testing
;

-- Original person record as JSON
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading original records from `person`' >&2
select person_id, null, null,
       'bx', 'record', null,
       json_object(
           --'person_id', person_id, -- selected
           'gender_concept_id', gender_concept_id, -- equivalent to `gender_source_value`
           'year_of_birth', year_of_birth, -- in `time_of_birth`
           'month_of_birth', month_of_birth, -- in `time_of_birth`
           'day_of_birth', day_of_birth, -- in `time_of_birth`
           'time_of_birth', time_of_birth, -- holds DOB, not time
           'race_concept_id', race_concept_id,
           'ethnicity_concept_id', ethnicity_concept_id,
           'location_id', location_id,
           'provider_id', provider_id,
           --'care_site_id', care_site_id, -- empty in the data
           --'person_source_value', person_source_value, -- empty in the data
           'gender_source_value', gender_source_value,
           --'gender_source_concept_id', gender_source_concept_id, -- empty in the data
           --'race_source_value', race_source_value, -- empty in the data
           --'race_source_concept_id', race_source_concept_id, -- empty in the data
           'ethnicity_source_value', ethnicity_source_value,
           'ethnicity_source_concept_id', ethnicity_source_concept_id
       )
from person
where person_id is not null
--limit 10 -- when testing
;

-- Insert events

-- Conditions
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading conditions from `condition_occurrence`' >&2
select person_id, condition_start_date, condition_end_date,
       'dx', condition_concept_id, null,
       json_object(
           'condition_occurrence_id', condition_occurrence_id,
           --'person_id', person_id, -- selected
           --'condition_concept_id', condition_concept_id, -- selected
           --'condition_start_date', condition_start_date, -- selected
           --'condition_start_datetime', condition_start_datetime, -- copies `condition_start_date`
           --'condition_end_date', condition_end_date, --selected
           --'condition_end_datetime', condition_end_datetime, -- empty in the data
           --'condition_type_concept_id', condition_type_concept_id, -- single value
           --'stop_reason', stop_reason, -- empty in the data
           'provider_id', provider_id,
           'visit_occurrence_id', visit_occurrence_id,
           'condition_source_value', condition_source_value
           --'condition_source_concept_id', condition_source_concept_id, --single value
           --'condition_status_source_value', condition_status_source_value, -- empty in the data
           --'condition_status_concept_id', condition_status_concept_id, -- empty in the data
       )
from condition_occurrence
where person_id is not null
  and condition_concept_id is not null
--limit 10 -- when testing
;

-- Deaths
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading deaths from `death`' >&2
select person_id, death_date, null,
       'xx', cause_concept_id, null,
       --json_object(
       --    --'person_id', person_id, -- selected
       --    --'death_date', death_date, -- selected
       --    --'death_datetime', death_datetime, -- copies `death_date`
       --    --'death_type_concept_id', death_type_concept_id, -- single value
       --    --'cause_concept_id', cause_concept_id, -- empty in the data
       --    --'cause_source_value', cause_source_value, -- empty in the data
       --    --'cause_source_concept_id', cause_source_concept_id -- empty in the data
       --)
       null -- omit JSON as it contains no additional information
from death
where person_id is not null
--limit 10 -- when testing
;

-- Drugs
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading drugs from `drug_exposure`' >&2
select person_id, drug_exposure_start_date, drug_exposure_end_date,
       'rx', drug_concept_id, null,
       json_object(
           'drug_exposure_id', drug_exposure_id,
           --'person_id', person_id, -- selected
           --'drug_concept_id', drug_concept_id, -- selected
           --'drug_exposure_start_date', drug_exposure_start_date, -- selected
           --'drug_exposure_start_datetime', drug_exposure_start_datetime, -- copies `drug_exposure_start_date`
           --'drug_exposure_end_date', drug_exposure_end_date, -- selected
           --'drug_exposure_end_datetime', drug_exposure_end_datetime, -- copies `drug_exposure_end_date`
           'verbatim_end_date', verbatim_end_date,
           'drug_type_concept_id', drug_type_concept_id,
           'stop_reason', stop_reason,
           'refills', refills,
           'quantity', quantity,
           'days_supply', days_supply,
           'sig', sig,
           --'route_concept_id', route_concept_id, -- empty in the data
           --'lot_number', lot_number, -- empty in the data
           'provider_id', provider_id,
           'visit_occurrence_id', visit_occurrence_id,
           'drug_source_value', drug_source_value,
           'drug_source_concept_id', drug_source_concept_id
           --'route_source_value', route_source_value, -- empty in the data
           --'dose_unit_source_value', dose_unit_source_value, -- empty in the data
       )
from drug_exposure
where person_id is not null
  and drug_concept_id is not null
--limit 10 -- when testing
;

-- Measurements (labs, vitals)
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading measurements from `measurement`' >&2
select person_id, measurement_date, measurement_date, -- Point interval
       'mx', measurement_concept_id, value_as_concept_id,
       json_object(
           'measurement_id', measurement_id,
           --'person_id', person_id, -- selected
           --'measurement_concept_id', measurement_concept_id, -- selected
           --'measurement_date', measurement_date, -- selected
           --'measurement_datetime', measurement_datetime, -- copies `measurement_date`
           --'measurement_type_concept_id', measurement_type_concept_id, -- single value
           'operator_concept_id', operator_concept_id,
           'value_as_number', value_as_number,
           --'value_as_concept_id', value_as_concept_id, -- selected
           'unit_concept_id', unit_concept_id,
           'range_low', range_low,
           'range_high', range_high,
           'provider_id', provider_id,
           'visit_occurrence_id', visit_occurrence_id,
           'measurement_source_value', measurement_source_value,
           --'measurement_source_concept_id', measurement_source_concept_id, -- empty in the data
           'unit_source_value', unit_source_value
           --'value_source_value', value_source_value, -- empty in the data
       )
from measurement
where person_id is not null
  and measurement_concept_id is not null
--limit 10 -- when testing
;

-- Observations (notes, environment, history, etc.)
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading observations from `observation`' >&2
select person_id, observation_date, observation_date, -- Point interval
       -- No meaningful value to include and only 3 unique
       -- `observation_concept_id`s
       'ox', observation_concept_id, null,
       json_object(
           'observation_id', observation_id,
           --'person_id', person_id, -- selected
           --'observation_concept_id', observation_concept_id, -- selected
           --'observation_date', observation_date, -- selected
           --'observation_datetime', observation_datetime, -- copies `observation_date`
           --'observation_type_concept_id', observation_type_concept_id, -- single value
           --'value_as_number', value_as_number, -- empty in the data
           --'value_as_string', value_as_string, -- empty in the data
           --'value_as_concept_id', value_as_concept_id, -- empty in the data
           --'qualifier_concept_id', qualifier_concept_id, -- empty in the data
           --'unit_concept_id', unit_concept_id, -- empty in the data
           --'provider_id', provider_id, -- empty in the data
           'visit_occurrence_id', visit_occurrence_id
           --'observation_source_value', observation_source_value, -- empty in the data
           --'observation_source_concept_id', observation_source_concept_id, -- empty in the data
           --'unit_source_value', unit_source_value, -- empty in the data
           --'qualifier_source_value', qualifier_source_value, -- empty in the data
       )
from observation
where person_id is not null
  and observation_concept_id is not null
--limit 10 -- when testing
;

-- Procedures
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading procedures from `procedure_occurrence`' >&2
select person_id, procedure_date, procedure_date, -- Point interval
       'px', procedure_concept_id, null,
       json_object(
           'procedure_occurrence_id', procedure_occurrence_id,
           --'person_id', person_id, -- selected
           --'procedure_concept_id', procedure_concept_id, -- selected
           --'procedure_date', procedure_date, -- selected
           --'procedure_datetime', procedure_datetime, -- copies `procedure_date`
           --'procedure_type_concept_id', procedure_type_concept_id, -- single value
           --'modifier_concept_id', modifier_concept_id, -- empty in the data
           --'quantity', quantity, -- empty in the data
           'provider_id', provider_id,
           'visit_occurrence_id', visit_occurrence_id,
           'procedure_source_value', procedure_source_value
           --'procedure_source_concept_id', procedure_source_concept_id, -- single value
           --'qualifier_source_value', qualifier_source_value, -- empty in the data
       )
from procedure_occurrence
where person_id is not null
  and procedure_concept_id is not null
--limit 10 -- when testing
;

-- Visits
.shell date +'%FT%T emr_to_events.sqlite.sql: Loading visits from `visit_occurrence`' >&2
select person_id, visit_start_date, visit_end_date,
       -- Visit type is the informative field (`visit_concept_id`
       -- contains only a single value)
       'vx', visit_type_concept_id, null,
       json_object(
           'visit_occurrence_id', visit_occurrence_id,
           --'person_id', person_id, -- selected
           --'visit_concept_id', visit_concept_id, -- single value
           --'visit_start_date', visit_start_date, -- selected
           --'visit_start_datetime', visit_start_datetime, -- copies `visit_start_date`
           --'visit_end_date', visit_end_date, -- selected
           --'visit_end_datetime', visit_end_datetime, -- copies `visit_end_date`
           --'visit_type_concept_id', visit_type_concept_id, -- selected
           --'provider_id', provider_id, -- empty in the data
           'care_site_id', care_site_id,
           --'admitting_source_concept_id', admitting_source_concept_id, -- empty in the data
           --'discharge_to_concept_id', discharge_to_concept_id, -- empty in the data
           'preceding_visit_occurrence_id', preceding_visit_occurrence_id
           --'visit_source_value', visit_source_value, -- empty in the data
           --'visit_source_concept_id', visit_source_concept_id, -- empty in the data
           --'admitting_source_value', admitting_source_value, -- empty in the data
           --'discharge_to_source_value', discharge_to_source_value, -- empty in the data
       )
from visit_occurrence
where person_id is not null
--limit 10 -- when testing
;

-- Done
.shell date +'%FT%T emr_to_events.sqlite.sql: Done generating events' >&2
