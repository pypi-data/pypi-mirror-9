from __future__ import division

import argparse
import logging
import re
import sys

from datetime import datetime
from datetime import timedelta

from weir import process, zfs


log = logging.getLogger(__name__)

# implement timedelta.total_seconds() for Python 2.6 support
def total_seconds(td):
	return ((td.days * 24 * 3600 + td.seconds) * 10**6
		+ td.microseconds) / 10**6

# destroy expired snapshots
def cull(filesystem, min_age=None, max_age=None,
		max_density=None, dry_run=False):
	# configure exclusions
	exclusions = []
	# keep all snapshots under min-age
	if min_age is not None:
		exclusions.append(lambda s: s['age'] < min_age)

	# configure filters
	filters = []
	# destroy all snapshots over max-age
	if max_age is not None:
		filters.append(lambda s: s['age'] > max_age)
	# destroy snapshots exceeding max-density
	# where density is defined as age / delta
	if max_density is not None:
		filters.append(lambda s: total_seconds(s['age']) \
			/ total_seconds(s['delta']) > max_density)

	# get snapshots as list of name, creation-time pairs
	# XXX: weir should provide values of correct type
	snapshots = [(prop['name'], datetime.fromtimestamp(float(prop['value'])))
		for prop in zfs.findprops(
			filesystem, max_depth=1, props=('creation',), types=('snapshot',))]

	# use most recent backup to calculate snapshot age
	latest = snapshots[-1][1]
	# use previous snapshot to calculate delta
	prev = None

	# always keep most recent snapshot
	for name, ctime in snapshots[:-1]:
		# create snapshot object to test against filters
		s = {
			'name': name,
			'ctime': ctime,
			'age': latest - ctime,
			'delta': abs(ctime - prev)
				if prev is not None else timedelta.max,
		}

		# skip if snapshot not eligible for destruction
		if (any(f(s) for f in exclusions)
				or not any(f(s) for f in filters)):
			prev = ctime
			continue

		# destroy snapshot
		log.info('destroying %s', name)
		if not dry_run:
			# ignore errors, eg due to held snapshot
			try:
				snapshot = zfs.ZFSSnapshot(name)
				snapshot.destroy()
			except process.DatasetBusyError:
				pass

# parse iso8601 time duration
def parse_timedelta(s):
	pattern = r'''^p?(?:(\d+)y)?(?:(\d+)m)?(?:(\d+)w)?(?:(\d+)d)?
		t?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$'''
	match = re.match(pattern, s, re.IGNORECASE|re.VERBOSE)
	if not match:
		raise ValueError(s)

	y, m, w, d, H, M, S = (int(x or 0) for x in match.groups())

	# approximate 1 year = 365.25 days and 1 month = 1/12 year
	d = y * 365.25 + m * 365.25 / 12 + w * 7 + d

	return timedelta(days=d, hours=H, minutes=M, seconds=S)

def main(argv=sys.argv):
	# set up command-line options
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('-n', '--dry-run', action='store_true')
	parser.add_argument('--min-age', type=parse_timedelta)
	parser.add_argument('--max-age', type=parse_timedelta)
	parser.add_argument('--max-density', type=float)
	parser.add_argument('filesystem')

	# parse command-line args
	try:
		args = parser.parse_args(argv[1:])
	except SystemExit:
		return 2

	# set log level - use WARNING by default
	log_level = max(logging.WARNING - (args.verbose * 10), logging.DEBUG)
	logging.basicConfig(level=log_level)

	# cull filesystems
	try:
		fs = args.filesystem
		cull(fs, args.min_age, args.max_age, args.max_density, args.dry_run)
		return 0
	except Exception as exc:
		log.error(exc)
		return 1

if __name__ == '__main__':
	sys.exit(main())
