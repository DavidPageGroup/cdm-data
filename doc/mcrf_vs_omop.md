Deviations of Marshfield data from OMOP CDM v5.3
================================================

The Marshfield data (as of February 15, 2018) CSV tables mostly follow the OMOP (Observational Medical Outcomes Partnership) CDM (Common Data Model), however, there are some discreptancies with version 5.3 of the CDM (most recent version as of February 15, 2018).

Clinical tables
---------------

Only a subset of the CDM Clinical Tables is present in the Marshfield data

| CDM v5.3 Clinical Table | CSV File (if present)
|-------------------------|-----------------------
| PERSON                  | omop_person_full.csv
| OBSERVATION_PERIOD      | 
| SPECIMEN                |
| DEATH                   |
| VISIT_OCCURRENCE        | omop_visit_occurence.csv
| PROCEDURE_OCCURENCE     | omop_procedure_occurence.csv
| DRUG_EXPOSURE           | omop_drug_exposure.csv, omop_drug_exposure_no_quotemarks.csv
| DEVICE_EXPOSURE         |
| CONDITION_OCCURENCE     | omop_condition_occurence.csv
| MEASUREMENT             | omop_measurement.csv
| NOTE                    |
| NOTE_NLP                |
| OBSERVATION             |
| FACT_RELATIONSHIP       |

There are also discreptancies in the fields present in the tables, these are listed below by table.

### PERSON

| Field                        | CDM v5.3 Specification | Present in CSV
|------------------------------|------------------------|---------------
| person_id                    | Required, integer      | Yes, as STUDY_ID
| gender_concept_id            | Required, integer      | Yes
| year_of_birth                | Required, integer      | Yes
| month_of_birth               | Optional, integer      | Yes
| day_of_birth                 | Optional, integer      | Yes
| birth_datetime               | Optional, datetime     | Yes, as TIME_OF_BIRTH (empty)
| race_concept_id              | Required, integer      | Yes
| ethnicity_concept_id         | Required, integer      | Yes
| location_id                  | Optional, integer      | Yes
| provider_id                  | Optional, integer      | Yes
| care_site_id                 | Optional, integer      | Yes (empty)
| person_source_value          | Optional, varchar(50)  | Yes (NULL)
| gender_source_value          | Optional, varchar(50)  | Yes
| gender_source_concept_id     | Optional, integer      | Yes (empty)
| race_source_value            | Optional, varchar(50)  | Yes
| race_source_concept_id       | Optional, integer      | Yes
| ethnicity_source_value       | Optional, varchar(50)  | Yes
| ethnicity_source_concept_id  | Optional, integer      | Yes

Note that CSV columns are in all caps.

-----

Copyright (c) 2018 Yuriy Sverchkov.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.

