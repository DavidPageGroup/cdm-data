#!/usr/bin/gawk -f

# Cleans the fields of the CDM-format data.  (Awk version, which is
# slightly faster than the Sed version.)

# Copyright (c) 2018 Aubrey Barnard.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.


# Setup
BEGIN {
    # Use the same output field separator as whatever was specified on
    # the command line
    OFS = FS
    # Use case-insensitive regexes
    IGNORECASE = 1
}

# Translate the fields in each line
{
    #print # See unaltered input record
    for (i = 1; i <= NF; i++) {
        # Replace "NULL", "* NOT AVAILABLE", and synonyms with empty
        # string
        if ($i ~ /^\s*(null|\*\s*not\s*available)\s*$/) {
            $i = ""
        } else {
            # Delete uninformative times
            $i = gensub(/\s*12:00:00\s*[AP]M\s*/, "", "g", $i)
            # Translate dates from '%m/%d/%Y' to '%Y-%m-%d' so that they
            # are sortable
            if (match($i, /^\s*([0-9]{1,2})\/([0-9]{1,2})\/([0-9]{4})\s*$/, groups)) {
                $i = sprintf("%04i-%02i-%02i", groups[3], groups[1], groups[2])
            }
        }
    }
    # Print cleaned record
    print
}
