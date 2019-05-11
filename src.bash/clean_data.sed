#!/usr/bin/sed -f

# Cleans the fields of the CDM-format data.  (Sed version.)

# Copyright (c) 2018 Aubrey Barnard.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.


# Delete fields containing NULL, "* NOT AVAILABLE", and synonyms.
# Multiple substitutions are needed to process overlapping matches.
s/^[[:space:]]*null[[:space:]]*,/,/gI
s/,[[:space:]]*null[[:space:]]*,/,,/gI
s/,[[:space:]]*null[[:space:]]*,/,,/gI
s/,[[:space:]]*null[[:space:]]*$/,/gI
s/,[[:space:]]*\*[[:space:]]*not[[:space:]]*available[[:space:]]*,/,,/gI

# Remove uninformative times
s/[[:space:]]*12:00:00[[:space:]]*[AP]M[[:space:]]*//gI

# Translate dates in '%m/%d/%Y' format to '%Y-%m-%d' so that they are
# sortable.  (The day and month need to be zero-padded.)
s/\<\([0-9]\{1,2\}\)\/\([0-9]\{1,2\}\)\/\([0-9]\{4\}\)\>/\3-0\1-0\2/g
s/\<\([0-9]\{4\}\)-0\?\([0-9]\{2\}\)-0\?\([0-9]\{2\}\)\>/\1-\2-\3/g
