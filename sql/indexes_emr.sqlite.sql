-- Definition of indexes for CDM clinical data, SQLite3 syntax

-- Copyright (c) 2018 Aubrey Barnard.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.

-- person
create index idx_person__pt  on person (person_id);
create index idx_person__sex on person (gender_concept_id);
create index idx_person__yob on person (year_of_birth);

-- condition_occurrence
create index idx_cond_occur__pt on condition_occurrence (person_id);
create index idx_cond_occur__id on condition_occurrence (condition_concept_id);
create index idx_cond_occur__dt on condition_occurrence (condition_start_date);

-- drug_exposure
create index idx_drug_exp__pt on drug_exposure (person_id);
create index idx_drug_exp__id on drug_exposure (drug_concept_id);
create index idx_drug_exp__dt on drug_exposure (drug_exposure_start_date);

-- measurement
create index idx_measrmnt__pt on measurement (person_id);
create index idx_measrmnt__id on measurement (measurement_concept_id);
create index idx_measrmnt__dt on measurement (measurement_date);

-- procedure_occurrence
create index idx_proc_occur__pt on procedure_occurrence (person_id);
create index idx_proc_occur__id on procedure_occurrence (procedure_concept_id);
create index idx_proc_occur__dt on procedure_occurrence (procedure_date);

-- visit_occurrence
create index idx_visit_occur__pt on visit_occurrence (person_id);
create index idx_visit_occur__id on visit_occurrence (visit_concept_id);
create index idx_visit_occur__dt on visit_occurrence (visit_start_date);
