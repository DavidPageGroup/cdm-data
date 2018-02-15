Deviations of Marshfield data from OMOP CDM v5.3
================================================

The Marshfield data (as of February 15, 2018) CSV tables mostly follow the OMOP (Observational Medical Outcomes Partnership) CDM (Common Data Model), however, there are some discreptancies with version 5.3 of the CDM (most recent version as of February 15, 2018).

OMOP CDM table and field specification and descriptions are taken from the [OMOP CDM Wiki]

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
Note that CSV columns are always in all caps.

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

### VISIT_OCCURENCE

| Field                         | CDM v.5.3 Specification | Present in CSV
|-------------------------------|-------------------------|---------------
| visit_occurence_id            | Required, integer       | Yes
| person_id                     | Required, integer       | Yes, as STUDY_ID
| visit_concept_id              | Required, integer       | Yes
| visit_start_date              | Required, date          | Yes
| visit_start_datetime          | Optional, datetime      | No
| VISIT_START_TIME              | Not in spec             | Yes (probably always 00:00)
| visit_end_date                | Required, date          | Yes (almost always empty)
| visit_end_datetime            | Optional, datetime      | No
| VISIT_END_TIME                | Not in spec             | Yes (almost always empty)
| visit_type_concept_id         | Required, integer       | Yes
| provider_id                   | Optional, integer       | Yes (always 0)
| care_site_id                  | Optional, integer       | Yes (always 0)
| visit_source_value            | Optional, varchar(50)   | Yes (always NULL)
| visit_source_concept_id       | Optional, integer       | Yes (empty)
| admitting_source_value        | Optional, varchar(50)   | No
| discharge_to_concept_id       | Optional, integer       | No
| discharge_to_source_value     | Optional, varchar(50)   | No
| preceding_visit_occurrence_id | Optional, integer       | No

* "Probably always," "always," and "empty" mean that I didn't see any other value briefly scrolling through the data
* "Almost always" means that I saw some other values, but they are rare.

### PROCEDURE_OCCURENCE

| Field                       | Required in CDM v5.3 | Type | Present in CSV | Description |
|-----------------------------|-----|-------------|------------------|------------|
| procedure_occurrence_id     | Yes | integer     | Yes              | A system-generated unique identifier for each Procedure Occurrence.|
| person_id                   | Yes | integer     | Yes, as STUDY_ID | A foreign key identifier to the Person who is subjected to the Procedure. The demographic details of that Person are stored in the PERSON table.|
| procedure_concept_id        | Yes | integer     | Yes              | A foreign key that refers to a standard procedure Concept identifier in the Standardized Vocabularies.|
| procedure_date              | Yes | date        | Yes              | The date on which the Procedure was performed.|
| procedure_datetime          | No  | datetime    | No               | The date and time on which the Procedure was performed.|
| procedure_type_concept_id   | Yes | integer     | Yes              | A foreign key to the predefined Concept identifier in the Standardized Vocabularies reflecting the type of source data from which the procedure record is derived.|
| modifier_concept_id         | No  | integer     | Yes (empty)      | A foreign key to a Standard Concept identifier for a modifier to the Procedure (e.g. bilateral)|
| quantity                    | No  | integer     | Yes (empty)      | The quantity of procedures ordered or administered.|
| provider_id                 | No  | integer     | Yes (empty)      | A foreign key to the provider in the PROVIDER table who was responsible for carrying out the procedure.|
| visit_occurrence_id         | No  | integer     | Yes              | A foreign key to the Visit in the VISIT_OCCURRENCE table during which the Procedure was carried out.|
| visit_detail_id             | No  | integer     | No               | A foreign key to the Visit Detail in the VISIT_DETAIL table during which the Procedure was carried out.|
| procedure_source_value      | No  | varchar(50) | Yes              | The source code for the Procedure as it appears in the source data. This code is mapped to a standard procedure Concept in the Standardized Vocabularies and the original code is, stored here for reference. Procedure source codes are typically ICD-9-Proc, CPT-4, HCPCS or OPCS-4 codes.|
| procedure_source_concept_id | No  | integer     | Yes              | A foreign key to a Procedure Concept that refers to the code used in the source.|
| modifier_source_value       | No  | varchar(50) | Yes (?), as QUANTIFIER_SOURCE_VALUE (always NULL) | The source code for the qualifier as it appears in the source data.|

### DRUG_EXPOSURE

Note that field order in the CSV differs from the order in this table

| Field | Required in CDM v5.3 | Type | Present in CSV | Description
|:------|:---------------------|:-----|:---------------|:-----------
| drug_exposure_id | Yes | integer | Yes | A system-generated unique identifier for each Drug utilization event.|
| person_id        | Yes | integer | Yes, as STUDY_ID | A foreign key identifier to the person who is subjected to the Drug. The demographic details of that person are stored in the person table.|
| drug_concept_id  | Yes | integer | Yes | A foreign key that refers to a Standard Concept identifier in the Standardized Vocabularies for the Drug concept.|
| drug_exposure_start_date | Yes | date | Yes | The start date for the current instance of Drug utilization. Valid entries include a start date of a prescription, the date a prescription was filled, or the date on which a Drug administration procedure was recorded.|
| drug_exposure_start_datetime | No | datetime | No | The start date and time for the current instance of Drug utilization. Valid entries include a start date of a prescription, the date a prescription was filled, or the date on which a Drug administration procedure was recorded.|
| drug_exposure_end_date | Yes | date | Yes (often empty) | The end date for the current instance of Drug utilization. It is not available from all sources.|
| drug_exposure_end_datetime | No | datetime | No | The end date and time for the current instance of Drug utilization. It is not available from all sources.|
| verbatim_end_date | No | date | No | The known end date of a drug_exposure as provided by the source|
| drug_type_concept_id | Yes| integer | Yes | A foreign key to the predefined Concept identifier in the Standardized Vocabularies reflecting the type of Drug Exposure recorded. It indicates how the Drug Exposure was represented in the source data.|
| stop_reason | No | varchar(20) | Yes (often empty) | The reason the Drug was stopped. Reasons include regimen completed, changed, removed, etc.|
| refills     | No | integer     | Yes (often empty) | The number of refills after the initial prescription. The initial prescription is not counted, values start with 0.|
| quantity    | No | float       | Yes (often empty) | The quantity of drug as recorded in the original prescription or dispensing record.|
| days_supply | No | integer      | Yes (often empty) | The number of days of supply of the medication as recorded in the original prescription or dispensing record.|
| sig         | No | varchar(MAX) | Yes (often empty) | The directions ("signetur") on the Drug prescription as recorded in the original prescription (and printed on the container) or dispensing record.|
| route_concept_id | No | integer | Yes (often empty) | A foreign key to a predefined concept in the Standardized Vocabularies reflecting the route of administration.|
| EFFECTIVE_DRUG_DOSE  | Not in spec | Unknown | Yes (often empty) | |
| DOSE_UNIT_CONCEPT_ID | Not in spec | Unknown | Yes (often empty) | |
| lot_number       | No | varchar(50) | Yes (often empty) | An identifier assigned to a particular quantity or lot of Drug product from the manufacturer.|
| provider_id      | No | integer     | Yes (empty) |A foreign key to the provider in the PROVIDER table who initiated (prescribed or administered) the Drug Exposure.|
| visit_occurrence_id | No | integer  | Yes         | A foreign key to the Visit in the VISIT_OCCURRENCE table during which the Drug Exposure was initiated.|
| visit_detail_id | No | integer | No | A foreign key to the Visit Detail in the VISIT_DETAIL table during which the Drug Exposure was initiated.|
| drug_source_value | No | varchar(50) | Yes | The source code for the Drug as it appears in the source data. This code is mapped to a Standard Drug concept in the Standardized Vocabularies and the original code is, stored here for reference.|
| drug_source_concept_id | No | integer | Yes (often empty) | A foreign key to a Drug Concept that refers to the code used in the source.|
| route_source_value | No | varchar(50) | Yes (often empty) | The information about the route of administration as detailed in the source.|
| dose_unit_source_value | No | varchar(50) | Yes (often empty) | The information about the dose unit as detailed in the source.|


-----

Copyright (c) 2018 Yuriy Sverchkov.  This is free software released under
the MIT License.  See `LICENSE.txt` for details.

[OMOP CDM Wiki]: https://github.com/OHDSI/CommonDataModel/wiki/
