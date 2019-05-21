# Extract features from a file of events and assemble them with a list
# of existing features to create a CSV file of feature function
# definitions suitable for use with the Python package
# `cdmdata.features`

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free software released under the MIT License
# (https://choosealicense.com/licenses/mit/).

# Check arguments
if [[ ${#} -gt 2 ]]; then
    echo "Error: Incorrect command line arguments" >&2
    echo "Usage: [(<events-file> | \"-\") [<features-file>]]" >&2
    exit 2
fi

events_file="${1:--}"
features_file="${2:-/dev/null}"

echo "$(date +'%FT%T') INFO: Extracting features from '${events_file}' and collecting with '${features_file}'" >&2
tail -n +2 "${events_file}" \
    | grep -v -e '|bx|' -e '|hx|' \
    | cut -d '|' -f 4,5 \
    | sort -t '|' -k 1,1 -k 2,2 -u --buffer-size=8G --parallel=8 \
    | awk -F '|' 'BEGIN { OFS = FS; } { print $1 "-" $2, $1, $2, "", "int", "count_events", ""; }' \
    | cat "${features_file}" - \
    | nl --number-width 1 --number-separator '|' \
    | cat <(echo 'id|name|tbl|typ|val|data_type|feat_func|args') -
echo "$(date +'%FT%T') INFO: Done collecting features" >&2
