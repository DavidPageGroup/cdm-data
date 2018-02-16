# Loads a collection of CDM format tables as CSV files into a SQLite
# database

# Copyright (c) 2018 Aubrey Barnard.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.

# Exit immediately on errors
set -e

# Process help options and exit
case ${1} in
    (-h|--help)
        echo "Usage: <data-dir> <db-file> <vocab-dir> <med-periods-dir>" >&2
        echo "       Arguments are optional but by position" >&2
        exit
        ;;
esac

# Log the given arguments as a message
function log() {
    echo "$(date +'%FT%T') ${prog_name}: ${@}" >&2
}

# Get command line arguments
prog_name=$(basename ${0:-load_tables.sqlite.sh})
data_dir=${1:-.}
db_file=${2:-db.sqlite}
vocab_dir=${3:-${data_dir}/vocab}
med_periods_dir=${4:-${data_dir}/med_periods}

# Set up files and directories
this_dir=$(dirname ${0})
src_dir=$(dirname ${this_dir})
sql_dir=${src_dir}/sql

log "Starting"

# Make sure created files are private
umask u=rwx,g=,o=

# Delete any existing database
if [[ -e ${db_file} ]]; then
    log "Deleting existing DB: '${db_file}'"
    rm ${db_file}
fi

# Create the tables
log "Creating tables"
sqlite3 ${db_file} < ${sql_dir}/tables_vocab.sqlite.sql
sqlite3 ${db_file} < ${sql_dir}/tables_clinic.sqlite.sql
sqlite3 ${db_file} < ${sql_dir}/tables_med_periods.sqlite.sql

# Information to enable loading the tables
tables=(
    # Vocabulary
    "domain                ${vocab_dir}/domain.csv                \t" # 1.2K
    "vocabulary            ${vocab_dir}/vocabulary.csv            \t" # 5.5K
    "concept_class         ${vocab_dir}/concept_class.csv         \t" #  14K
    "relationship          ${vocab_dir}/relationship.csv          \t" #  31K
    "drug_strength         ${vocab_dir}/drug_strength.csv         \t" # 127M
    "concept_synonym       ${vocab_dir}/concept_synonym.csv       \t" # 437M
    "concept               ${vocab_dir}/concept.csv               \t" # 569M
    "concept_relationship  ${vocab_dir}/concept_relationship.csv  \t" # 1.4G
    "concept_ancestor      ${vocab_dir}/concept_ancestor.csv      \t" # 2.5G

    # Data
    "person                ${data_dir}/omop_person_full.csv           ,"  # 217M
    "visit_occurrence      ${data_dir}/omop_visit_occurrence.csv      ,"  # 5.8G
    "condition_occurrence  ${data_dir}/omop_condition_occurrence.csv  ,"  #  16G
    "procedure_occurrence  ${data_dir}/omop_procedure_occurrence.csv  ,"  #  26G
    "drug_exposure         ${data_dir}/omop_drug_exposure.csv         ,"  #  27G
    "measurement           ${data_dir}/omop_measurement.csv           ,"  #  77G

    # Med periods
    "duloxetine_periods  ${med_periods_dir}/duloxetine_med_periods.csv  ," # 434K
    "bupropion_periods   ${med_periods_dir}/bupropion_med_periods.csv   ," # 613K

)

for tbl_tup in "${tables[@]}"; do
    #echo "tbl_tup: '${tbl_tup}'"
    read -r tbl_nm tbl_file tbl_dlim <<< ${tbl_tup}
    #echo "tbl_nm: '${tbl_nm}'; tbl_file: '${tbl_file}'; tbl_dlim: '${tbl_dlim}';"
    log "Loading table '${tbl_nm}' from file '${tbl_file}'"
    /usr/bin/time -v sqlite3 ${db_file} <<EOF
.separator "${tbl_dlim}"
.import "${tbl_file}" "${tbl_nm}"
-- Delete header that was loaded
delete from "${tbl_nm}" where rowid = 1;
EOF
    log "Done loading '${tbl_nm}'"
done
log "End"
