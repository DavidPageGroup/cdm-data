# How to clean, sort, and compress the CDM-format data

# Copyright (c) 2018 Aubrey Barnard, Jon Badger.  This is free software
# released under the MIT License.  See `LICENSE.txt` for details.

# Usage: bash <path-to>/clean_sort_compress_data.sh <src> <dst> &> clean_sort_compress_data.$(date +'%Y%m%d-%H%M%S').log

# Exit immediately on errors
set -e

# Essential directories and variables
prog_name="$(basename ${0})"
script_dir="$(dirname ${0})"

# Print a timestamped message to stderr
function log {
    echo "$(date +'%FT%T') ${prog_name}: ${@}" >&2
}

# Get the command line arguments
src_dir=${1:-$(pwd)}
dst_dir=${2:-$(pwd)/clean_data}

# Check the command line arguments
if [[ ${src_dir} =~ ^--?h(elp)?$ ]]; then
    echo "Usage: bash ${prog_name} [<src-dir> [<dest-dir>]]"
    exit 0
fi
if [[ ! -d ${src_dir} || ! -r ${src_dir} || ! -x ${src_dir} ]]; then
    log "ERROR: Not a readable directory: ${src_dir}"
    exit 1
fi

log "Starting"

# Make sure destination directory exists
mkdir -p ${dst_dir}

# Make sure temporary directory exists and is private
export TMPDIR=/scratch/${USER}/tmp
mkdir -p ${TMPDIR}
chmod go= ${TMPDIR}

# Make directories absolute
src_dir=$(cd ${src_dir}; pwd)
dst_dir=$(cd ${dst_dir}; pwd)

# Make a list of all generated files
declare -a dst_files

# Time the sorting and compression
#timer_cmd=
timer_cmd="/usr/bin/time -v"

# Sort the data by study ID and compress it (this needs a machine with
# >120G, many threads, and fast NFS access or else don't run the sorts
# in parallel or decrease the resources requested)
log "Starting to clean, sort, and compress CSVs in '${src_dir}' into '${dst_dir}'"
for file in $(find ${src_dir}/ -maxdepth 1 -iname '*.csv'); do
    base_name=$(basename ${file})
    # Remove extraneous information from filenames
    dst_file=${base_name,,} # Make lowercase
    dst_file=${dst_file/omop_/} # Remove "omop_" prefix
    dst_file=${dst_file/person_full/person}
    dst_file=${dst_dir}/${dst_file} # Make full path
    # Set which field is the study ID
    case ${base_name} in
        # Fact tables.  First field is numeric ID.
        ( omop_care_site.csv \
            | omop_death.csv \
            | omop_location.csv \
            | omop_person_full.csv )
            sort_keys="--key=1,1n"
            ;;
        # Event tables.  Second field is subject ID, fourth field is
        # event date.
        ( omop_condition_occurrence.csv \
            | omop_drug_exposure.csv \
            | omop_measurement.csv \
            | omop_observation.csv \
            | omop_procedure_occurrence.csv \
            | omop_visit_occurrence.csv )
            sort_keys="--key=2,2n --key=4,4"
            ;;
        # Example tables.  First field is subject ID, second and third
        # fields are dates (or, for raw data, the third field is drug
        # name, but it's ok to also sort on that).
        ( bupropion*.csv \
            | duloxetine*.csv )
            sort_keys="--key=1,1n --key=2,3"
            ;;
        (*)
            log "WARNING: Skipping processing unrecognized file: '${file}'"
            continue
            ;;
    esac
    # Make sure source and destination files are different.  (Don't
    # clobber source files!)
    if [[ "${file}" -ef "${dst_file}" ]]; then
        log "WARNING: Skipping processing of identical source and destination files: '${file}' -> '${dst_file}'"
        continue
    fi
    # Record the destination file
    dst_files[${#dst_files[@]}]="${dst_file}"
    # Clean up double quotes in literal-format CSV files
    sub_dblqt=
    if [[ ${base_name} == omop_drug_exposure.csv ]]; then
        sub_dblqt="-e 's/\"/\'\'/g'"
    fi
    # Sort and compress each file in parallel.  Sleep briefly between
    # each to hopefully avoid cluttering output.
    {
        log "Starting to clean and sort '${file}'"
        # Change to Unix EOLs (delete "CR" from "CRLF"; `dos2unix`
        # doesn't work as a filter) and clean the fields.  Then sort by
        # patient ID.  For GNU Awk (GAWK) version < 4.0 --re-interval is
        # required to accomodate regular expressions with intervals.
        # Remove the header before processing and reinstate it after.
        ${timer_cmd} tail -n +2 ${file} \
            | ${timer_cmd} sed -e 's/\r//g' ${sub_dblqt} \
            | ${timer_cmd} awk --re-interval  -F , \
                  -f ${script_dir}/clean_data.awk \
            | ${timer_cmd} sort --stable --field-separator=, \
                  --buffer-size=10G --temporary-directory=${TMPDIR} \
                  ${sort_keys} \
            | cat <(head -n 1 ${file} \
                        | sed -e 's/\r//g') - > ${dst_file}
        log "Done cleaning and sorting '${file}'"
        # Compress in various ways to allow for different size /
        # decompress speed trade-offs.  Do all compression in parallel.
        ${timer_cmd} xz -9 -c --threads=8 ${dst_file} > ${dst_file}.xz &
        sleep 1
        ${timer_cmd} gzip -9 -c ${dst_file} > ${dst_file}.gz &
        sleep 1
        ${timer_cmd} lz4 -9 -c ${dst_file} > ${dst_file}.lz4 &
        sleep 1
    } &
    sleep 1
done

# Wait for all of above jobs to complete
wait
log "Done cleaning, sorting, and compressing CSVs"

log "Checking for remaining dirt"
# Check if cleaning successful.  Analyze remaining quotes, placeholders,
# and other dirt.  Turn off exiting on error because `grep` returns 1
# when it does not find a match (which is good in this case).
set +e
for file in "${dst_files[@]}"; do
    # Print lines with an odd number of double quotes.  These are the
    # lines to check for proper CSV syntax.  Using `grep` as below is
    # faster than `awk -F '"' '{if (((NF - 1) % 2) != 0) print}'`.
    grep -n '^[^"]*"\([^"]*"[^"]*"\)*[^"]*$' ${file} > ${file}.dblqts &
    # See if anything was missed that should have been deleted
    grep -ni 'null\|not *available' ${file} > ${file}.nulls &
    grep -n '12:00:00' ${file} > ${file}.badtimes &
    grep -n '\(,\|^\)[[:space:]]*[0-9]\+/[0-9]\+/[0-9]\+[[:space:]]*\(,\|$\)' ${file} > ${file}.baddates &
done
wait
# Remove empty files (which leaves only those files with actual dirt)
find ${dst_dir}/ -type f -empty -delete
log "Done checking for dirt"
log "All done"
