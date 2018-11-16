# Summarize the data in a SQLite DB given the table definitions

# Copyright (c) 2018 Aubrey Barnard.  This is free software released
# under the MIT License.  See `LICENSE.txt` for details.


import argparse
import collections
import io
import logging
import pathlib
import re
import sqlite3
import sys

import yaml


# Patterns for parsing table definitions

_table_def_beg_pattern = re.compile(
    r'\bcreate\s+table\b', re.IGNORECASE)

_table_def_end_pattern = re.compile(r'\)\s*;')

_table_def_pattern = re.compile(
    r'\bcreate\s+table\s+(\S+)\s+\(([^()]*)\)\s*;',
    re.IGNORECASE)


def find_table_defs(sql_lines):
    """
    Find the table definitions in the given SQL input (a sequence of
    strings).  Yield each complete table definition as a string.

    Naïvely assumes that "create table" starts a table definition, that
    ");" ends it, that each of the previous occur on a single line, and
    that it is OK to ignore quoting, escaping, and context.
    """
    # Gather lines into table definitions and parse them
    tbl_def = io.StringIO()
    line = next(sql_lines, None)
    while line is not None:
        # Look for the beginning of a table definition
        beg_match = _table_def_beg_pattern.search(line)
        # If not found, go to the next line
        if beg_match is None:
            line = next(sql_lines, None)
            continue
        # The start has been found.  Now look for the end.
        end_match = _table_def_end_pattern.search(line, beg_match.end())
        while end_match is None:
            # Accumulate the current line into the buffer
            if beg_match is None:
                tbl_def.write(line)
            else:
                tbl_def.write(line[beg_match.start():])
                beg_match = None
            # Get the next line
            line = next(sql_lines, None)
            if line is None:
                # EOF in middle of table definition
                return
            end_match = _table_def_end_pattern.search(line)
        # The end has been found.  Add it to the buffer.
        if beg_match is None:
            tbl_def.write(line[:end_match.end()])
        else:
            tbl_def.write(line[beg_match.start():end_match.end()])
            beg_match = None
        # Yield the table definition
        yield tbl_def.getvalue()
        # Reset the buffer
        tbl_def = io.StringIO()
        # Process the rest of the line
        line = line[end_match.end():]


def parse_table_column_names(table_definition_text):
    """
    Parse the table and column names from the given SQL table
    definition.  Return (table-name, (col1-name, col2-name, ...)).

    Naïvely assumes that ","s separate column definitions regardless of
    quoting, escaping, and context.
    """
    match = _table_def_pattern.match(table_definition_text)
    if match is None:
        raise ValueError('Cannot parse table definition from: {!r}'
                         .format(table_definition_text))
    tbl_nm = match[1]
    col_defs = match[2].split(',')
    col_nms = (col_def.split(maxsplit=1)[0] for col_def in col_defs)
    return (tbl_nm, tuple(col_nms))


def run_query(db, query, params=None):
    logging.getLogger(__name__).info(
        'Running query:\n    {};\n  with parameters:\n    {}'
        .format(query, params))
    cursor = db.cursor()
    cursor.arraysize = 1024
    if params is None:
        cursor.execute(query)
    else:
        cursor.execute(query, params)
    return cursor


def n_rows(db, tbl_nm, *args, **kwargs):
    rows = run_query(
        db,
        'select count(*) from {}'.format(tbl_nm),
    ).fetchall()
    return rows[0][0]


def n_vals(db, tbl_nm, col_nm, *args, **kwargs):
    rows = run_query(
        db,
        'select count(*) from (select distinct {} from {})'
        .format(col_nm, tbl_nm),
    ).fetchall()
    return rows[0][0]


def top_k_vals(db, tbl_nm, col_nm, top_k=10, *args, **kwargs):
    rows = run_query(
        db,
        'select count(*) as count, {col} from {tbl} '
        'group by {col} order by count desc limit ?'
        .format(tbl=tbl_nm, col=col_nm),
        (top_k,),
    ).fetchall()
    return rows


def summarize_table(
        db,
        table_name,
        col_names=None,
        tab_info=('n_rows',),
        col_info=('n_vals', 'top_k_vals'),
        top_k=10,
):
    """
    This function is susceptible to SQL injection attacks via invalid
    table or column names.  You are responsible for sanitizing table and
    column names.  This was implemented this way because no standard
    Python library provides functionality for quoting SQL identifiers
    and the `sqlite3` module does not allow parameterizing table or
    column names.
    """
    glbls = globals()
    # Table summary
    tbl_summary = collections.OrderedDict()
    # Gather table summary information in the order requested
    for info_nm in tab_info:
        tbl_summary[info_nm] = glbls[info_nm](db, table_name)
    # Columns summary
    cols_summary = collections.OrderedDict()
    for col_nm in col_names:
        col_summary = collections.OrderedDict()
        # Gather column summary information in the order requested
        for info_nm in col_info:
            col_summary[info_nm] = glbls[info_nm](
                db, table_name, col_nm, top_k=top_k)
        if col_summary:
            cols_summary[col_nm] = col_summary
    if cols_summary:
        tbl_summary['columns'] = cols_summary
    return tbl_summary


def _odict_repr(dumper, odict):
    return dumper.represent_dict(odict.items())
yaml.add_representer(collections.OrderedDict, _odict_repr)


def _tuple_repr(dumper, tupl):
    return dumper.represent_list(tupl)
yaml.add_representer(tuple, _tuple_repr)


def print_table_summaries_as_yaml(tables_to_summaries, file=sys.stdout, **yaml_dump_kwargs):
    print('%YAML 1.2\n---', file=file)
    top = {'tables': tables_to_summaries}
    yaml.dump(top, file, **yaml_dump_kwargs)
    print('...', file=file)


def configure_logging(level=logging.INFO, stream=sys.stderr):
    logging.basicConfig(
        style='{',
        format='{asctime} {levelname} {name}: {message}',
        datefmt='%Y-%m-%dT%H:%M:%S',
        level=level,
        stream=stream,
    )


def configure_sqlite3(
        db,
        n_threads=4,
        mmap_size=(2 * 2 ** 30), # 2 GiB
        cache_size=(4 * 2 ** 30), # 4 GiB
):
    # Unfortunately, pragmas don't work with the "?" parameter syntax,
    # so use formatting instead
    run_query(db, 'pragma threads = {}'.format(n_threads))
    run_query(db, 'pragma mmap_size = {}'.format(mmap_size))
    # Convert cache size to KiB
    run_query(db, 'pragma cache_size = -{}'.format(cache_size // 1024))
    # Log the values
    logger = logging.getLogger(__name__)
    n_threads = run_query(db, 'pragma threads').fetchall()
    if n_threads:
        n_threads = n_threads[0][0]
    mmap_size = run_query(db, 'pragma mmap_size').fetchall()[0][0]
    cache_size = run_query(db, 'pragma cache_size').fetchall()[0][0]
    logger.info('Using SQLite threads: {}'.format(n_threads))
    logger.info('Using SQLite mmap size: {}'.format(mmap_size))
    logger.info('Using SQLite page cache size: {}'.format(cache_size))


def main_api(
        # Required arguments
        sql_filename,
        db_filename,

        # Reporting control
        top_k=10,

        # SQLite control
        sqlite3_n_threads=4,
        sqlite3_mmap_size=(2 * 2 ** 30), # 2 GiB
        sqlite3_cache_size=(4 * 2 ** 30), # 4 GiB

        # System control
        prog_name=__name__,
        log_level=logging.INFO,
        stdout=sys.stdout,
        stderr=sys.stderr,
):
    configure_logging(level=log_level, stream=stderr)
    logger = logging.getLogger(prog_name)
    logger.info('Starting')
    # Read the table definitions
    logger.info('Reading table definitions from: {!r}'
                .format(sql_filename))
    with open(sql_filename, 'rt') as sql_lines:
        tables = [parse_table_column_names(d)
                  for d in find_table_defs(sql_lines)]
    logger.info('Found {} table definitions'.format(len(tables)))
    # Connect to the SQLite DB
    logger.info('Connecting to SQLite DB: {!r}'.format(db_filename))
    with sqlite3.connect(db_filename) as db:
        configure_sqlite3(
            db,
            n_threads=sqlite3_n_threads,
            mmap_size=sqlite3_mmap_size,
            cache_size=sqlite3_cache_size,
        )
        table_summaries = collections.OrderedDict()
        for tbl_nm, col_nms in tables:
            logger.info('Summarizing table: {}'.format(tbl_nm))
            summary = summarize_table(db, tbl_nm, col_nms, top_k=top_k)
            table_summaries[tbl_nm] = summary
    # Print report
    logger.info('Printing report')
    print_table_summaries_as_yaml(table_summaries, file=stdout)
    logger.info('Done')


def main_cli(prog_name, *args):
    # Use basename for program name
    prog_name = pathlib.Path(prog_name).name
    # Set up basic CLI
    arg_prsr = argparse.ArgumentParser(
        prog=prog_name,
        description='Summarize the data in a SQLite 3 DB',
    )
    arg_prsr.add_argument('sql_filename')
    arg_prsr.add_argument('db_filename')
    arg_prsr.add_argument('--top_k', type=int, metavar='N')
    arg_prsr.add_argument('--sqlite3_n_threads', type=int, metavar='N')
    arg_prsr.add_argument('--sqlite3_mmap_size', type=int, metavar='SZ')
    arg_prsr.add_argument('--sqlite3_cache_size', type=int, metavar='SZ')
    # Parse arguments
    nmspc = arg_prsr.parse_args(args)
    # Convert argument parser namespace to a dictionary.  Remove unset
    # values to avoid overwriting defaults.
    env = {k: v for (k, v) in vars(nmspc).items() if v is not None}
    # Run
    main_api(prog_name=prog_name, **env)
    return 0


if __name__ == '__main__':
    sys.exit(main_cli(*sys.argv))
