# Creates and loads a SQLite DB for either (1) OMOP vocabulary data, (2)
# CDM-format EMR data, or (3) task examples

# Copyright (c) 2018 Aubrey Barnard.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.

# Exit immediately on errors
set -e

# Process command line arguments
case ${1} in
    # Help or no arguments
    (-h|--help|"")
        echo "Usage: (emr|exs|vocab) [<data-dir> [<db-file>]]" >&2
        exit
        ;;
    (emr|exs)
        tbl_dlim=,
        ;;
    (vocab)
        tbl_dlim="\\t"
        ;;
    (*)
        echo "Unrecognized command line argument: '${1}'" >&2
        exit 2
        ;;
esac

# Log the given arguments as a message
function log() {
    echo "$(date +'%FT%T') ${prog_name}: ${@}" >&2
}

# Get command line arguments
prog_name=$(basename ${0:-make_db.sqlite.sh})
data_dir=${2:-.}
db_file=${3:-${1}.sqlite}

# Set up files and directories
this_dir=$(dirname ${0})
src_dir=$(dirname ${this_dir})
sql_dir=${src_dir}/sql

log "Start loading ${1} DB"

# Make sure created files are private
umask u=rwx,g=,o=

# Delete any existing database
if [[ -e ${db_file} ]]; then
    log "Deleting existing DB: '${db_file}'"
    rm ${db_file}
fi

# Create the tables
log "Creating tables"
sqlite3 ${db_file} < ${sql_dir}/tables_${1}.sqlite.sql

# Get the names of the tables
tbl_nms=$(grep -i 'create[[:space:]]\+table' ${sql_dir}/tables_${1}.sqlite.sql | awk '{print $3}')

# Load the tables.  Do separate sqlite3 calls so that loading each table
# can be timed.
for tbl_nm in ${tbl_nms}; do
    tbl_file="${data_dir}/${tbl_nm}.csv"
    log "Loading table '${tbl_nm}' from file '${tbl_file}'"
    /usr/bin/time -v sqlite3 ${db_file} <<EOF
.separator "${tbl_dlim}"
.import "${tbl_file}" "${tbl_nm}"
-- Delete header that was loaded
delete from "${tbl_nm}" where rowid = 1;
EOF
    log "Done loading '${tbl_nm}'"
done

# Create indexes (if any are specified)
if [[ -e ${sql_dir}/indexes_${1}.sqlite.sql ]]; then
    log "Creating indexes"
    sqlite3 ${db_file} < ${sql_dir}/indexes_${1}.sqlite.sql
fi

log "End"
