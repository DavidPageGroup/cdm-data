# Extract events and facts from a CDM-format EMR DB, sort them, and dump
# them as CSV to standard output.  The events can then be loaded into a
# SQLite DB using `make_db.sqlite.sh`.

# Copyright (c) 2018 Aubrey Barnard.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.

# Run like:
# $ bash dump_events.sqlite.sh path/to/emr.sqlite
# or, with a custom SQLite:
# $ SQLITE3=~/opt/bin/sqlite3 bash dump_events.sqlite.sh ...

# Exit immediately on errors
set -e

# Exit with a message and a status
function die() {
    echo -e "${1}" >&2
    exit "${2:-1}"
}

# Log the given arguments as a message
function log() {
    echo "$(date +'%FT%T') ${prog_name}: ${@}" >&2
}

# Check command line arguments
[[ ${#} -ne 1 ]] && die "Error: Bad command line arguments\nUsage: <emr-db>" 2
[[ ! -e "${1}" ]] && die "Error: DB does not exist: ${1}" 1

# Get command line arguments
prog_name=$(basename ${0:-dump_events.sqlite.sh})
emr_db="${1}"

# Set up files and directories
this_dir="$(dirname ${0})"
src_dir="$(dirname ${this_dir})"

log "Start"

# Get environment variables
sqlite3_exec="${SQLITE3:-sqlite3}"
mmap_size=${SQLITE3_MMAP_SIZE:-$((2 * 2 ** 30))} # 2 GiB

# Log environment variables / configuration
log "SQLite executable: ${sqlite3_exec}"
log "SQLite mmap size: ${mmap_size}"

# Use a private temporary directory with lots of space
TMPDIR="$(mktemp -d /scratch/$USER/tmp.dump_events.XXXXX)"
chmod go= "${TMPDIR}"
export TMPDIR
log "Using temporary directory: ${TMPDIR}"

# Generate events from CDM EMR DB, sort them, and dump them to standard
# output.  Don't use the `-echo` or `-stats` options even though they
# would be nice because they go to stdout (as well as stderr).
"${sqlite3_exec}" --mmap ${mmap_size} -bail -readonly \
    "${emr_db}" < "${src_dir}/sql/emr_to_events.sqlite.sql" |
    # Since event types (field 5) can be numbers or strings, sort by
    # both
    sort --stable --field-separator='|' --parallel=8 \
    --buffer-size=50% --temporary-directory=${TMPDIR} \
    --key=1,1n --key=2,2 --key=3,3 --key=4,4 \
    --key=5,5g --key=5,5 --key=6,6 --key=7,7 |
    # Add header
    cat <(echo 'id|lo|hi|tbl|typ|val|jsn') -

# Delete temporary directory
if [[ -e "${TMPDIR}" ]]; then
    log "Deleting temporary directory: ${TMPDIR}"
    rm -R "${TMPDIR}"
fi

log "Done"
