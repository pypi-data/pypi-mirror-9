import argparse
import logging
import sys

from weir import zfs

from .copy import copy


log = logging.getLogger(__name__)

# synchronise snapshots on source and destination datasets
def sync(src, dst, intermediates=False, recursive=False, force=False):
	if recursive:
		raise NotImplementedError()

	# get all source snapshots
	is_snapshot = isinstance(src, zfs.ZFSSnapshot)
	src_snaps = src.parent().snapshots() if is_snapshot else src.snapshots()

	# find index of source snapshot if specified
	n = len(src_snaps) - 1
	if is_snapshot:
		while n >= 0:
			if src_snaps[n].name == src.name: break
			n -= 1
		else:
			raise AssertionError("snapshot not found in parent's children")

	# source and destination snapshot names must match for sync
	if '@' in dst:
		raise Exception('cannot specify destination snapshot name')

	# find earlier snapshots not present in destination
	try:
		dst_snaps = set(s.snapname() for s in zfs.open(dst).snapshots())
	except zfs.DatasetNotFoundError:
		m = -1
	else:
		m = n
		while m >= 0:
			if src_snaps[m].snapname() in dst_snaps: break
			m -= 1

	# send full snapshot if no common ancestor found
	# note: don't mount new filesystem to avoid need for -F later
	if m < 0 and n >= 0:
		m = 0 if intermediates else n
		copy(src_snaps[m], dst, force=force, nomount=True)

	# send incremental snapshots up to specified snapshot
	if intermediates >= 2:
		# legacy mode: send each snapshot separately
		for i in xrange(m+1, n+1):
			copy(src_snaps[i], dst, base=src_snaps[i-1].name, force=force)
	elif m < n:
		# normal mode: send one single- or multi-snapshot stream
		copy(src_snaps[n], dst, base=src_snaps[m].name,
			intermediates=intermediates, force=force)

	# update snapshot holds
	try:
		# tag src snapshots with destination dataset name
		tag = 'sluice.sync:' + dst

		# place hold on synced source snapshot
		if n >= 0:
			src_snaps[n].hold(tag)

		# release any previous holds
		for i in xrange(n):
			try:
				src_snaps[i].release(tag)
			except zfs.HoldTagNotFoundError:
				pass
	except zfs.HoldTagExistsError:
		pass

def main(argv=sys.argv):
	# set up command-line options
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='count', default=0)
#	parser.add_argument('-n', '--dry-run', action='store_true')
	parser.add_argument('-F', '--force', action='store_true')

	parser.add_argument('-r', '--recursive', action='store_true')
	parser.add_argument('-I', '--intermediates', action='count', default=0)

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

	# sync source to destination
	try:
		src = zfs.open(args.src)
		sync(src, args.dst, intermediates=args.intermediates,
			recursive=args.recursive, force=args.force)
		return 0
	except Exception as exc:
		log.error(exc)
		return 1

if __name__ == '__main__':
	sys.exit(main())
