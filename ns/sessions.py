import argparse, sys, heapq, logging, os
from collections import namedtuple
from menagerie.iteration import sequence
from menagerie.formatting import tsv

from mwutil.lib import sessions

logger = logging.getLogger("nettrom_sessions.ns.sessions")

def main():
	def revisions_file(f):
		if not f.isatty():
			return (rev for rev in RevisionReader(f) if rev.timestamp != None)
		
	def sessions_file(f):
		return Writer(f)
	
	def session_revisions_file(f):
		return RevisionWriter(f)
	
	parser = argparse.ArgumentParser(
		description='''
			Takes a chonological list of revisions (not sorted by page) and generates session 
			information into one (or two) output files.  To create the dataset
			that this script reads, call "revisions" with no "--by_page" 
			grouping.
		''',
		conflict_handler="resolve"
	)
	parser.add_argument(
		'sources',
		nargs="*",
		type=lambda path:revisions_file(open(path, "r")), 
		help='files containing revisions sorted by timestamp (defaults to stdin)',
		default=[revisions_file(sys.stdin)]
	)
	parser.add_argument(
		'--sessions',
		type=lambda path:sessions_file(open(path, 'w')), 
		help='an output file to write sessions to (defaults to stdout)',
		default=sessions_file(sys.stdout)
	)
	parser.add_argument(
		'--session_revisions',
		type=lambda path:session_revisions_file(open(path, 'w')), 
		help='an output file to write annotated revisions to (optional)'
	)
	parser.add_argument(
		'--cutoff',
		type=int,
		help="session cutoff (in seconds).  (defaults to 1 hour=3600 seconds)",
		default=3600
	)
	parser.add_argument(
		'--quiet',
		help="Quiet verbose reporting?",
		action="store_true", 
		default=False
	)
	parser.add_argument(
		'--debug',
		help="Debugging output?",
		action="store_true", 
		default=False
	)
	args = parser.parse_args()
	
	logging.basicConfig(
			level=logging.DEBUG if args.debug else logging.INFO,
			stream=sys.stderr,
			datefmt='%H:%M:%S',
			format='%(asctime)s %(name)-8s %(message)s'
	)
	
	run(args.sources, args.cutoff, args.sessions, args.session_revisions,  not args.quiet, args.debug)



def run(sources, cutoff, session_writer, session_revisions_writer, verbose, debug):
	
	user_session_counts = {}
	
	def write_session(user, revs):
		if user in user_session_counts:
			index = user_session_counts[user] + 1
		else:
			index = 0
			
			user_session_counts[user] = index
		
		session_writer.write([
			user.id,
			user.text,
			index,
			len(revs),
			revs[0].id,
			revs[-1].id,
			revs[0].timestamp,
			revs[-1].timestamp
		])
		
		
		
		if session_revisions_writer != None:
			prev_timestamp = None
			for i, rev in enumerate(revs):
				session_revisions_writer.write([
					rev.id,
					rev.page_id,
					rev.user_id,
					rev.user_text,
					index,
					i,
					rev.timestamp,
					prev_timestamp
				])
				prev_timestamp = rev.timestamp
	
	
	logger.info("Grouping revisions into sessions.")
	if verbose: logger.info("{0}={1}".format("verbose", verbose))
	logger.debug("%s=%s" % ("cutoff", cutoff))
	
	cache = sessions.Cache(cutoff=cutoff)
	
	last_rev = None
	revs = enumerate(sequence(*sources, 
	                           compare=lambda r1,r2:(r1.timestamp, r1.id or 0) <= \
	                                                (r2.timestamp, r2.id or 0)))
	for i, rev in revs:
		if last_rev != None and last_rev.timestamp > rev.timestamp:
			raise AssertionError("Revisions not sorted by timestamp.  Are they sorted by page?")
		
		if verbose:
			if i % 80000 == 0: sys.stderr.write("%06d: " % i)
			if i % 1000 == 0: sys.stderr.write(".")
			if (i+1) % 80000 == 0: sys.stderr.write("\n")
		
		for user, session_revs in cache.process(User(rev.user_id, rev.user_text), 
		                                        rev.timestamp, rev):
			write_session(user, session_revs)
		
		last_rev = rev
		
	
	for user, session_revs in cache.get_active_sessions():
		write_session(user, session_revs)
	

User = namedtuple("User", ['id', 'text'])

def Writer(f):
	return tsv.Writer(
		f,
		headers=[
			'user_id',
			'user_text',
			'session_index',
			'revisions',
			'first_id',
			'last_id',
			'first_timestamp',
			'last_timestamp'
		]
	)

def RevisionReader(f):
	return tsv.Reader(f,
		types=[
			int, #id
			int, #page_id
			int, #user_id
			str, #user_text
			str, #timestamp
			str, #sha1
			int, #len
			tsv.robust_bool, #deleted
			tsv.robust_bool #archived
		],
		log_errors=True # This deals with weird stderr output
	)

def RevisionWriter(f):
	return tsv.Writer(
		f,
		headers=[
			'id',
			'page_id',
			'user_id',
			'user_text',
			'timestamp',
			'session_index',
			'session_ordinal'
		]
	)
	

if __name__ == "__main__": main()