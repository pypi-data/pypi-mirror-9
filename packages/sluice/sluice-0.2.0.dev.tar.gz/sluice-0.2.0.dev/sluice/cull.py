import argparse
import logging
import re
import subprocess
import sys

from datetime import datetime
from datetime import timedelta

from weir import zfs


log = logging.getLogger(__name__)

# get snapshots as list of name, timestamp pairs
def _snapshots(filesystem):
	snapshots = zfs._list([filesystem], depth=1,
		props=('name', 'creation'), types=('snapshot',))

	# format used for zfs creation time property
# XXX: get rid of this and use zfs get -p to get unix timestamp instead
	ZFS_TIMESTAMP_FORMAT = '%a %b %d %H:%M %Y'
	parse_zfs_time = lambda t: datetime.strptime(t, ZFS_TIMESTAMP_FORMAT)

	return [(s['name'], parse_zfs_time(s['creation'])) for s in snapshots]

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
		filters.append(lambda s: s['age'].total_seconds() \
			/ s['delta'].total_seconds() > max_density)

	# get snapshots
	snapshots = _snapshots(filesystem)

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
			snapshot = zfs.open(name)
			# ignore errors, eg due to held snapshot
			try:
				snapshot.destroy()
			except zfs.DatasetBusyError:
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
# XXX: no error if no filesystems specified
	parser.add_argument('filesystem', nargs=argparse.REMAINDER)

	# parse args into dict
	try:
# XXX: don't use vars()?
		args = vars(parser.parse_args(argv[1:]))
	except SystemExit:
		return 2

	# set log level - use WARNING by default
	log_level = max(logging.WARNING - (args.pop('verbose') * 10), logging.DEBUG)
	logging.basicConfig(level=log_level)

	# cull filesystems
	try:
		for filesystem in args.pop('filesystem'):
			log.info('culling %s', filesystem)
			cull(filesystem, **args)
		return 0
	except Exception as exc:
		log.error(exc)
		return 1

if __name__ == '__main__':
	sys.exit(main())
