-- Definition of indexes for CDM vocabulary data, SQLite3 syntax

-- Copyright (c) 2018 Aubrey Barnard.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.

-- concept
create index idx_concept__id on concept (concept_id);

-- concept_ancestor
create index idx_cncpt_ancs__ancs on concept_ancestor (ancestor_concept_id);
create index idx_cncpt_ancs__desc on concept_ancestor (descendant_concept_id);

-- concept_class
create index idx_cncpt_cls__id on concept_class (concept_class_id);

-- concept_relationship
create index idx_cncpt_rel__id1 on concept_relationship (concept_id_1);
create index idx_cncpt_rel__id2 on concept_relationship (concept_id_2);
create index idx_cncpt_rel__rel on concept_relationship (relationship_id);

-- concept_synonym
create index idx_cncpt_syn__id on concept_synonym (concept_id);

-- domain
create index idx_domain__id on domain (domain_id);

-- drug_strength
create index idx_drug_strength__id on drug_strength (drug_concept_id);

-- relationship
create index idx_relationship__id on relationship (relationship_id);

-- vocabulary
create index idx_vocabulary__id on vocabulary (vocabulary_id);
