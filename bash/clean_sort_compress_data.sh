# How to clean, sort, and compress the CDM-format data
#
# Copyright (c) 2018 DPRG CDM Data.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.

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

# Sort the data by study ID and compress it (this needs a machine with
# >120G, many threads, and fast NFS access or else don't run the sorts
# in parallel or decrease the resources requested)
for file in $(find ${src_dir} -maxdepth 1 -iname 'omop_*.csv' -not -iname '*no_quote*'); do
    if [[ $(basename ${file}) == omop_person_full.csv ]]; then
        key=1,1n # First field is study ID
    else
        key=2,2n # Second field is study ID
    fi
    sort --stable --field-separator=, --buffer-size=20G --temporary-directory=${TMPDIR} --key=${key} ${file} | xz --threads=8 > ${dst_dir}/$(basename ${file}).xz &
done

# Clean and sort the medication lists
for file in $(find ${meds_dir} -maxdepth 1 -iname '*.csv'); do
    # Remove uninformative "12:00:00 AM"s from the dates
    sed -e 's/ 12:00:00 AM//g' ${file} | sort --stable --field-separator=, --buffer-size=1G --temporary-directory=${TMPDIR} --key=1,1n | xz > ${dst_dir}/$(basename ${file}).xz &
done

# Wait for all of above jobs to complete
wait

# Analyze double quotes
for file in $(find ${dst_dir} -maxdepth 1 -iname '*.csv.xz'); do
    xzcat ${file} | grep -n '"' > ${file}.dblqts &
done
# Remove empty files
find ${dst_dir} -empty -delete
