import argparse
import logging
import sys

from weir import zfs


log = logging.getLogger(__name__)

# copy zfs snapshots using send and receive
def copy(src, dst, base=None, intermediates=False,
		replicate=False, properties=False, deduplicate=False,
		append_path=False, append_name=False, force=False, nomount=False):
	# open zfs stream from source
	with src.send(base=base, intermediates=intermediates,
			replicate=replicate, properties=properties, deduplicate=deduplicate) as f:
		# receive zfs stream into destination
		zfs.receive(dst, append_path=append_path, append_name=append_name,
			force=force, nomount=nomount, file=f)

def main(argv=sys.argv):
	# set up command-line options
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='count', default=0)
#	parser.add_argument('-n', '--dry-run', action='store_true')
	parser.add_argument('-F', '--force', action='store_true')

	# stream options
	parser.add_argument('-R', '--replicate', action='store_true')
	parser.add_argument('-D', '--deduplicate', action='store_true')
	parser.add_argument('-p', '--properties', action='store_true')

	# destination options
	append_args = parser.add_mutually_exclusive_group()
	append_args.add_argument('-d', '--append-path', action='store_true')
	append_args.add_argument('-e', '--append-name', action='store_true')
	parser.add_argument('-u', '--no-mount', action='store_true')

	# incremental base
	base_args = parser.add_mutually_exclusive_group()
	base_args.add_argument('-i', metavar='base', dest='inc_base')
	base_args.add_argument('-I', metavar='base', dest='int_base')

	# source and destination
	parser.add_argument('src')
	parser.add_argument('dst')

	# parse command-line args
	try:
		args = parser.parse_args(argv[1:])
	except SystemExit:
		return 2

	# set log level - use WARNING by default
	log_level = max(logging.WARNING - (args.verbose * 10), logging.DEBUG)
	logging.basicConfig(level=log_level)

	# interpret incremental snapshot options
	intermediates = (args.int_base is not None)
	base = args.int_base if intermediates else args.inc_base

	# copy datasets
	try:
		src = zfs.open(args.src)
		copy(src, args.dst, base, intermediates,
			args.replicate, args.properties, args.deduplicate,
			args.append_path, args.append_name, args.force, args.no_mount)
		return 0
	except Exception as exc:
		log.error(exc)
		return 1

if __name__ == '__main__':
	sys.exit(main())
