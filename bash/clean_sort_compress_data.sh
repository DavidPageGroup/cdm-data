# How to clean, sort, and compress the CDM-format data
#
# Copyright (c) 2018 DPRG CDM Data.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.

# Exit immediately on errors
set -e

# Directories given as variables on the command line given prior to the
# script.  That is, invoke like this:
# `src_dir=/a/b dst_dir=/c/d bash clean_sort_compress_data.sh`.
src_dir=${src_dir:=$(pwd)}
meds_dir=${src_dir}/GenericDrug
dst_dir=${dst_dir:=${HOME}/cleaned_sorted_data}

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
    # Sort and compress each file in parallel
    {
        # Change to Unix EOLs, remove uninformative times from the dates
        # before sorting
        sed -e 's/\r//g' -e 's/ 12:00:00 AM//g' ${file} | ${timer_cmd} sort --stable --field-separator=, --buffer-size=20G --temporary-directory=${TMPDIR} --key=${key} > ${dst_file}
        # Compress in various ways to allow for different size /
        # decompress speed trade-offs.  Do all compression in parallel.
        ${timer_cmd} xz -9 -c --threads=8 ${dst_file} > ${dst_file}.xz &
        ${timer_cmd} gzip -9 -c ${dst_file} > ${dst_file}.gz &
        ${timer_cmd} lz4 -9 -c ${dst_file} > ${dst_file}.lz4 &
    } &
done

# Wait for all of above jobs to complete
wait

# Analyze quotes
for file in $(find ${dst_dir} -maxdepth 1 -iname '*.csv'); do
    grep -n '"' ${file} > ${file}.dblqts &
    grep -n "'" ${file} > ${file}.sglqts &
done
wait
# Remove empty files
find ${dst_dir} -empty -delete
