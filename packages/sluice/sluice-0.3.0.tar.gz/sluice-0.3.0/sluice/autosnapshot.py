import argparse
import logging
import sys

from datetime import datetime

from weir import zfs


log = logging.getLogger(__name__)

# ISO 8601 compliant default timestamp format
DEFAULT_FORMAT = '%Y-%m-%dT%H%M'

# zfs property holding the preferred timestamp format
FORMAT_PROPERTY = 'sluice.autosnapshot:format'

def autosnapshot(filesystem, format=None, recursive=False, props={}):
	if not format:
		format = filesystem.getpropval(FORMAT_PROPERTY, DEFAULT_FORMAT)

	snapname = datetime.now().strftime(format)

	log.info('creating new snapshot %s@%s', filesystem.name, snapname)
	return filesystem.snapshot(snapname, recursive, props)

def parse_prop(s):
	name, _, value = s.partition('=')
	return name, value

def main(argv=sys.argv):
	# set up command-line options
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('-r', '--recursive', action='store_true')
	parser.add_argument('-o', metavar='property=value',
		dest='props', default=[], action='append', type=parse_prop)
	parser.add_argument('snapshot', metavar='filesystem[@snapformat]')

	# parse command-line args
	try:
		args = parser.parse_args(argv[1:])
	except SystemExit:
		return 2

	# set log level - use WARNING by default
	log_level = max(logging.WARNING - (args.verbose * 10), logging.DEBUG)
	logging.basicConfig(level=log_level)

	# create snapshot
	try:
		template = zfs.ZFSSnapshot(args.snapshot)
		dataset = template.parent()
		format = template.snapname()

		recursive = args.recursive
		props = dict(args.props)

		autosnapshot(dataset, format, recursive, props)
		return 0
	except Exception as exc:
		log.error(exc)
		return 1

if __name__ == '__main__':
	sys.exit(main())
