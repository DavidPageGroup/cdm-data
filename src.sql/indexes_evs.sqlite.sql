-- Definition of indexes for events, SQLite3 syntax

-- Copyright (c) 2018 Aubrey Barnard.  This is free software released
-- under the MIT License.  See `LICENSE.txt` for details.


-- Event sequence (person / patient) ID
create index idx_ev__id on ev (id);

-- Event occurrence interval
create index idx_ev__lo on ev (lo);
create index idx_ev__hi on ev (hi);

-- Event type
create index idx_ev__tbl on ev (tbl);
create index idx_ev__typ on ev (typ);
