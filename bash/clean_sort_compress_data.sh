# How to clean, sort, and compress the CDM-format data

# Copyright (c) 2018 Aubrey Barnard.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.

# Exit immediately on errors
set -e

# Directories given as variables on the command line given prior to the
# script.  That is, invoke like this:
# `src_dir=/a/b dst_dir=/c/d bash clean_sort_compress_data.sh &> clean_sort_compress_data.$(date +'%Y%m%d-%H%M%S').log`
src_dir=${src_dir:=$(pwd)}
meds_dir=${src_dir}/GenericDrug
dst_dir=${dst_dir:=${HOME}/cleaned_sorted_data}

# Other directories and variables
prog_name="$(basename ${0})"
script_dir="$(dirname ${0})"

function log {
    echo "$(date +'%FT%T') ${prog_name}: ${@}" >&2
}
log "Starting"

# Make sure destination directory exists
mkdir -p ${dst_dir}

# Make sure temporary directory exists and is private
export TMPDIR=/scratch/${USER}/tmp
mkdir -p ${TMPDIR}
chmod go-rwx ${TMPDIR}

# Time the sorting and compression
#timer_cmd=
timer_cmd="/usr/bin/time -v"

# Sort the data by study ID and compress it (this needs a machine with
# >120G, many threads, and fast NFS access or else don't run the sorts
# in parallel or decrease the resources requested)
log "Starting to clean, sort, and compress CSVs in '${src_dir}' and '${meds_dir}' into '${dst_dir}'"
for file in $(find ${src_dir} -maxdepth 1 -iname 'omop_*.csv' -not -iname '*no_quote*') $(find ${meds_dir} -maxdepth 1 -iname '*.csv'); do
    base_name=$(basename ${file})
    dst_file=${dst_dir}/${base_name}
    # Set which field is the study ID
    case ${basename} in
        (omop_person_full.csv|bupropion*.csv|duloxetine*.csv)
            key=1,1n # First field is study ID
            ;;
        (*)
            key=2,2n # Second field is study ID
            ;;
    esac
    # Clean up double quotes in literal-format CSV files
    sub_dblqt=
    if [[ ${basename} == omop_drug_exposure.csv ]]; then
        sub_dblqt="-e 's/\"/\'\'/g'"
    fi
    # Sort and compress each file in parallel.  Sleep briefly between
    # each to hopefully avoid cluttering output.
    {
        log "Starting to clean and sort '${file}'"
        # Change to Unix EOLs (delete "CR" from "CRLF"; `dos2unix`
        # doesn't work as a filter) and clean the fields.  Then sort by
        # patient ID.
        ${timer_cmd} sed -e 's/\r//g' ${sub_dblqt} ${file} | ${timer_cmd} awk -F , -f ${script_dir}/clean_data.awk | ${timer_cmd} sort --stable --field-separator=, --buffer-size=10G --temporary-directory=${TMPDIR} --key=${key} > ${dst_file}
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
for file in $(find ${dst_dir} -maxdepth 1 -iname '*.csv'); do
    # Print lines with an odd number of double quotes.  These are the
    # lines to check for proper CSV syntax.  Using `grep` as below is
    # faster than `awk -F '"' '{if (((NF - 1) % 2) != 0) print}'`.
    grep '^[^"]*"\([^"]*"[^"]*"\)*[^"]*$' ${file} > ${file}.dblqts &
    # See if anything was missed that should have been deleted
    grep -ni 'null\|not *available' ${file} > ${file}.nulls &
    grep -n '12:00:00' ${file} > ${file}.badtimes &
    grep -n '[0-9]\+/[0-9]\+/[0-9]\+' ${file} > ${file}.baddates &
done
wait
# Remove empty files (which leaves only those files with actual dirt)
find ${dst_dir} -empty -delete
log "Done checking for dirt"
log "All done"
