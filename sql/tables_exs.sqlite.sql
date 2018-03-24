-- Definition of tables to hold examples (medication periods) for
-- various tasks, SQLite3 syntax

-- Copyright (c) 2018 Aubrey Barnard.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.

create table bupropion_med_periods (
    person_id int,
    "from" text,
    upto text,
    dose real,
    label text
);

create table duloxetine_med_periods (
    person_id int,
    "from" text,
    upto text,
    dose real,
    label text
);
