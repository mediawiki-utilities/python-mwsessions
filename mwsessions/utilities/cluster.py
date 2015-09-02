"""
Clusters activities into sessions.  Expects the first two columns to represent
'timestamp' and 'user' respectively.

Usage:
    cluster -h | --help
    cluster [<source>...] [--sessions=<path>] [--events=<path>]
            [--cutoff=<secs>] [--verbose] [--debug]
            [--user=<col>...]
            [--timestamp=<col>]

Options:
    -h --help         Prints this documentation
    <source>          Path to a ordered file containing timed events.  Multiple
                      sources will be sequenced together.  If no source is
                      specified, <stdin> will be read.
    --sessions=<path> Path to a file to write session events
                      [default: <stdout>]
    --events=<path>   If specified, a path to a file to write annotated events
    --cutoff=<secs>   A cutoff to use for session delimiting in seconds
                      [default: 3600]
    --user=<col>      If specified, then use these column as a user identifier.
                      [default: user]
    --timestamp=<col> If specified, use this column as the timestamp and expect
                      it to be sorted. [default: timestamp]
    --verbose         Print dots and stuff
    --debug           Print a bunch of logging information
"""
import traceback
import io
import logging
import sys
from collections import namedtuple

import docopt
from more_itertools import peekable
from mw.lib import sessions

import mysqltsv

logger = logging.getLogger("mwsessions.utilities.cluster")

SESSION_SUFFIX = ['start', 'end', 'index', 'events']
EVENT_SUFFIX = ['prev_timestamp', 'session_start', 'session_end',
                'session_index', 'session_events', 'event_index']

def log_error(lineno, line, error):
    logger.error("An error occurred while processing line {0}".format(line))
    logger.error(repr(line))
    logger.error(traceback.format_exc())


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    if len(args['<source>']) > 0:
        sources = [mysqltsv.Reader(open(p, errors='replace'), error_handler=log_error)
                   for p in args['<source>']]
    else:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8',
                                        errors='replace')
        sources = [mysqltsv.Reader(input_stream, error_handler=log_error)]

    user_cols = args['--user']
    timestamp_col = args['--timestamp']
    cutoff = float(args['--cutoff'])

    if args['--sessions'] == "<stdout>":
        session_writer = mysqltsv.Writer(sys.stdout,
                                         headers=user_cols + SESSION_SUFFIX)
    else:
        session_writer = mysqltsv.Writer(open(args['--sessions'], 'w'),
                                         headers=user_cols + SESSION_SUFFIX)

    if args['--events'] is not None:
        event_writer = mysqltsv.Writer(open(args['--events'], 'w'),
                                         headers=sources[0].headers + \
                                                 EVENT_SUFFIX)
    else:
        event_writer = None

    verbose = args['--verbose']
    debug = args['--debug']

    run(sources, cutoff, session_writer, event_writer, user_cols, timestamp_col,
        verbose, debug)

def run(sources, cutoff, session_writer, event_writer, user_cols, timestamp_col,
        verbose, debug):

    logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            stream=sys.stderr,
            datefmt='%H:%M:%S',
            format='%(asctime)s %(name)-8s %(message)s'
    )
    user_session_counts = {}

    def write_session(user, events):
        if user in user_session_counts:
            session_index = user_session_counts[user] + 1
        else:
            session_index = 0

        user_session_counts[user] = session_index

        session_writer.write(list(user) + [
            events[0][timestamp_col],
            events[-1][timestamp_col],
            session_index,
            len(events),
        ])



        if event_writer != None:
            prev_timestamp = None
            for event_index, event in enumerate(events):
                event_writer.write(
                    event.values() + [
                        prev_timestamp,
                        events[0][timestamp_col], # session_start
                        events[-1][timestamp_col], # session_end
                        session_index,
                        len(events),
                        event_index
                    ]
                )
                prev_timestamp = event[timestamp_col]


    if verbose: logger.info("{0}={1}".format("verbose", verbose))
    logger.debug("%s=%s" % ("cutoff", cutoff))

    cache = sessions.Cache(cutoff=cutoff)

    last_event = None
    events = sequence(
        *sources,
        compare=lambda e1,e2:e1[timestamp_col] <= \
                             e2[timestamp_col]
    )
    for i, event in enumerate(events):
        if last_event is not None and last_event.timestamp > event.timestamp:
            raise RuntimeError("Events not sorted by timestamp.  " +
                               "Comparing {0} < {1}".format(last_event, event))

        if verbose:
            if i % 80000 == 0:
                sys.stderr.write("%06d: " % i)
                sys.stderr.flush()
            if i % 1000 == 0:
                sys.stderr.write(".")
                sys.stderr.flush()
            if (i+1) % 80000 == 0:
                sys.stderr.write("\n")
                sys.stderr.flush()

        user = tuple(event[col] for col in user_cols)
        timestamp = event[timestamp_col]

        for user, session_events in cache.process(user, timestamp, event):
            write_session(user, session_events)

        last_event = event


    for user, session_events in cache.get_active_sessions():
        write_session(user, session_events)



def sequence(*iterables, **kwargs):

    compare = kwargs.get('compare', lambda i1,i2:i1<i2)
    iterables = [peekable(it) for it in iterables]

    done = False
    while not done:

        next_i = None

        for i, it in enumerate(iterables):
            if it: # Not empty
                if next_i == None or \
                   compare(it.peek(), iterables[next_i].peek()):
                    next_i = i

        if next_i == None:
            done = True
        else:
            yield next(iterables[next_i])


if __name__ == "__main__": main()
