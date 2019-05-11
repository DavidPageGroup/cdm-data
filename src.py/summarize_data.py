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


def read_table_definitions(sql_filename):
    logger = logging.getLogger(__name__)
    logger.info('Reading table definitions from: {!r}'
                .format(sql_filename))
    with open(sql_filename, 'rt') as sql_lines:
        table_definitions = [parse_table_column_names(d)
                             for d in find_table_defs(sql_lines)]
    logger.info('Found {} table definitions'
                .format(len(table_definitions)))
    return table_definitions


def run_query(db, query, params=None):
    logging.getLogger(__name__).info(
        'Running query:\n    {}\n  with parameters:\n    {}'
        .format(query, params))
    cursor = db.cursor()
    cursor.arraysize = 1024
    if params is None:
        cursor.execute(query)
    else:
        cursor.execute(query, params)
    return cursor


def unpack_scalars(rows):
    if len(rows) == 1 and len(rows[0]) == 1:
        return rows[0][0]
    else:
        return rows


def q_n_rows(tbl_nm, *args, **kwargs):
    return ('select count(*) from {};'.format(tbl_nm), None)


def q_n_vals(tbl_nm, col_nm, *args, **kwargs):
    return ('select count(*) from (select distinct {} from {});'
            .format(col_nm, tbl_nm), None)


def q_top_k_vals(tbl_nm, col_nm, top_k=10, *args, **kwargs):
    return ('select count(*), {col} from {tbl} '
            'group by {col} order by count(*) desc limit ?;'
            .format(tbl=tbl_nm, col=col_nm), (top_k,))


def generate_setup_queries(
        n_threads=4,
        mmap_size=(2 * 2 ** 30), # 2 GiB
        cache_size=(4 * 2 ** 30), # 4 GiB
):
    yield (None, 'pragma threads = {};'.format(n_threads))
    yield ('Using SQLite threads', 'pragma threads;')
    yield (None, 'pragma mmap_size = {};'.format(mmap_size))
    yield ('Using SQLite mmap size', 'pragma mmap_size;')
    yield (None, 'pragma cache_size = -{};'.format(cache_size // 1024))
    yield ('Using SQLite page cache size', 'pragma cache_size;')


def generate_summary_queries(
        table_definitions,
        tab_info=('n_rows',),
        col_info=('n_vals', 'top_k_vals'),
        top_k=10,
):
    glbls = globals()
    for tbl_nm, col_nms in table_definitions:
        # Query table summary information in the order requested
        for info_nm in tab_info:
            q_nm = 'q_' + info_nm
            yield (tbl_nm, None, info_nm, glbls[q_nm](tbl_nm))
        for col_nm in col_nms:
            # Query column summary information in the order requested
            for info_nm in col_info:
                q_nm = 'q_' + info_nm
                yield (tbl_nm, col_nm, info_nm, glbls[q_nm](
                    tbl_nm, col_nm, top_k=top_k))


def print_queries(
        setup_queries,
        summary_queries,
        header=None,
        mk_log=False,
        file=sys.stdout,
):
    if header is not None:
        print(header, file=file)
    print('\n-- Setup queries', file=file)
    if mk_log:
        print(".shell date +'%FT%T sqlite3: Setting up'", file=file)
    for _, q in setup_queries:
        print(q, file=file)
    print('\n-- Summary queries', file=file)
    if mk_log:
        print(".shell date +'%FT%T sqlite3: Summarizing data'", file=file)
    prev_tbl_nm = None
    for q_def in summary_queries:
        tbl_nm, col_nm, info_nm, (q, p) = q_def
        if tbl_nm != prev_tbl_nm:
            print('\n-- Summarizing table: {}'.format(tbl_nm),
                  file=file)
            if mk_log:
                print(".shell date +'%FT%T sqlite3: Summarizing table: {}'"
                      .format(tbl_nm), file=file)
            prev_tbl_nm = tbl_nm
        if p:
            # Naïvely substitute parameters
            q = q.replace('?', '{}').format(*p)
        if mk_log:
            print(".shell date +'%FT%T sqlite3: Running query: {}'"
                  .format(q), file=file)
        print(q, file=file)
    if mk_log:
        print("\n.shell date +'%FT%T sqlite3: Done'", file=file)


def execute_queries(
        db_filename,
        setup_queries,
        summary_queries,
):
    # Create a dictionary with 3 levels: tables, columns, and infos
    summaries = collections.OrderedDict()
    # Connect to the SQLite DB
    logger = logging.getLogger(__name__)
    logger.info('Connecting to SQLite DB: {!r}'.format(db_filename))
    with sqlite3.connect(db_filename) as db:
        logger.info('Running setup queries')
        for msg, q in setup_queries:
            rows = run_query(db, q).fetchall()
            if msg:
                logger.info('{}: {}'.format(msg, unpack_scalars(rows)))
        logger.info('Running summary queries')
        prev_tbl_nm = None
        for q_def in summary_queries:
            tbl_nm, col_nm, info_nm, (q, p) = q_def
            if tbl_nm != prev_tbl_nm:
                logger.info('Summarizing table: {}'.format(tbl_nm))
                prev_tbl_nm = tbl_nm
            rows = run_query(db, q, p).fetchall()
            # Get the right part of the summaries for attaching this
            # information.  Using `setdefault` is a very wasteful way of
            # querying and building structure in this case, but
            # creatingi an "ordered default dict" is too complicated.
            summary = summaries
            if tbl_nm:
                summary = summary.setdefault(
                    tbl_nm, collections.OrderedDict())
            if col_nm:
                summary = summary.setdefault(
                    col_nm, collections.OrderedDict())
            summary[info_nm] = unpack_scalars(rows)
        logger.info('Done executing queries')
    return summaries


def _odict_repr(dumper, odict):
    return dumper.represent_dict(odict.items())
yaml.add_representer(collections.OrderedDict, _odict_repr)


def _tuple_repr(dumper, tupl):
    return dumper.represent_list(tupl)
yaml.add_representer(tuple, _tuple_repr)


def print_table_summaries_as_yaml(
        tables_to_summaries, file=sys.stdout, **yaml_dump_kwargs):
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


def main_api(
        # Required arguments
        sql_filename,
        db_filename,

        # Mode
        print_mode=False,

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
    # Set `__name__` so that loggers using the typical
    # `getLogger(__name__)` will have a meaningful name.  Hopefully this
    # won't be a problem for anything else.
    global __name__
    __name__ = prog_name
    configure_logging(level=log_level, stream=stderr)
    logger = logging.getLogger(__name__)
    logger.info('Starting')
    # Read the table definitions
    tbl_defs = read_table_definitions(sql_filename)
    # Generate queries for all summary information
    init_qs = list(generate_setup_queries(
        n_threads=sqlite3_n_threads,
        mmap_size=sqlite3_mmap_size,
        cache_size=sqlite3_cache_size,
    ))
    main_qs = list(generate_summary_queries(tbl_defs, top_k=top_k))
    # Output queries or execute them and collect the results ourselves?
    if print_mode:
        header = """
-- Queries for summaring the data in the tables defined in:
-- {!r}

-- Run like:
-- $ sqlite3 -bail -echo -header -readonly {!r} < this_script.sql
""".strip().format(sql_filename, db_filename)
        print_queries(
            init_qs,
            main_qs,
            header=header,
            mk_log=(log_level <= logging.INFO),
            file=stdout,
        )
    else:
        table_summaries = execute_queries(db_filename, init_qs, main_qs)
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
    arg_prsr.add_argument('sql_filename', metavar='SQL-FILE')
    arg_prsr.add_argument('db_filename', metavar='DB-FILE')
    arg_prsr.add_argument('--print', action='store_true',
                          dest='print_mode')
    arg_prsr.add_argument('--top-k', type=int, metavar='N',
                          dest='top_k')
    arg_prsr.add_argument('--sqlite3-n-threads', type=int, metavar='N',
                          dest='sqlite3_n_threads')
    arg_prsr.add_argument('--sqlite3-mmap-size', type=int, metavar='SZ',
                          dest='sqlite3_mmap_size')
    arg_prsr.add_argument('--sqlite3-cache-size', type=int, metavar='SZ',
                          dest='sqlite3_cache_size')
    arg_prsr.add_argument('--log-level', type=int, metavar='LVL',
                          dest='log_level')
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
