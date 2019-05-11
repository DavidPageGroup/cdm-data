-- Definition of table to hold events, SQLite3 syntax

-- Copyright (c) 2018 Aubrey Barnard.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.


create table ev (
    -- Event sequence (person / patient) ID
    id int not null,

    -- Event occurrence interval.  Either end can be open (null).  If
    -- both ends are open, it is a "fact".  Use strings in formats
    -- compatible with SQLite date / time functions:
    -- https://www.sqlite.org/lang_datefunc.html.
    lo text, -- Start (lo) date / time
    hi text, -- End (hi) date / time

    -- Event type
    tbl text not null, -- Name of originating table
    typ int not null, -- ID in originating table (CDM concept ID)

    -- Event / Fact value
    val text,

    -- Remaining fields from original row as a JSON dictionary
    jsn text -- Don't conflict with `json` in SQLite
);
