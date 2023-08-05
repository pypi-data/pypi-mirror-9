# TODO: simplify - make a simple wrapper for rsync + zfs snapshot
# - allow src, dst, and arbitrary rsync args to be specified (and snapshot args?)
# - allow cmd to be replaced by cp, ditto etc? - ie --cp='rsync -a --xattrs --foo'
#   - probably best to use rsync as default, scp would work in a compatible manner?
# - use autosnapshot if destination snapshot not specified
# - maintain compatibility with remote rsync using ssh or rsyncd
# - don't allow remote zfs dataset - could use rsyncd + post-xfer exec for that case
# eg zfs import --exclude="**/tmp" example.com:/path/to/src dataset@snapname

# requirements
# call rsync && zfs [auto]snapshot
# options:
# -r: required for rsync, probably send to zfs as well (could switch off with --no-recursive-snapshot)
# -o: rsync owner - use long option for zfs property (--prop / --snapshot-property) 
# -f: rsync filter rule - use long option for zfs snapshot format (--timestamp-format)
# organisation / usage simplification:
# - store the import source as a property of the zfs filesystem
# - store rsync args as property of zfs filesystem

# is this too much work - easier to call sh -c rsync ... && zfs [auto]snapshot ... ?
# - simplify by only allowing long options for zfs-only options
#   - can parse argv and remove these long options
# - what about -r?

import argparse
import logging
import pipes
import subprocess
import sys

# get logger for module
log = logging.getLogger(__name__)

# parse username@hostname:path as tuple of netloc, path
def parse_scp_url(url):
	# netloc is url up to first colon not containing '/'
	i = url.find(':')
	if i >= 0 and url.find('/', 0, i) < 0:
		netloc, path = url[:i], url[i+1:]
	else:
		netloc, path = '', url

	return netloc, path

# parse volume@snapshot as tuple of volume, snapshot
def parse_snapshot(dataset):
	netloc, _ = parse_scp_url(dataset)
	i = dataset.find('@', len(netloc))
	if i >= 0:
		volume, snapshot = dataset[:i], dataset[i+1:]
	else:
		volume, snapshot = dataset, ''

	return volume, snapshot

# prepare command for remote execution
def remote_cmd(cmd, hostname, username=None, remote_shell=None):
	# don't attempt remote shell if command or hostname empty
	if not cmd or not hostname:
		return cmd

	# don't use remote shell for localhost unless user is specified
	if not username and hostname in {'localhost', '127.0.0.1'}:
		return cmd

	# use ssh as default remote shell
	if not remote_shell:
		rsh_cmd = ['ssh']
	elif isinstance(remote_shell, basestring):
		rsh_cmd = [remote_shell]
	else:
		rsh_cmd = list(remote_shell)

	# set remote user and host
	if username:
		rsh_cmd.append('-l')
		rsh_cmd.append(username)
	rsh_cmd.append(hostname)

	# quote command for remote shell if provided as list
	if isinstance(cmd, basestring):
		rsh_cmd.append(cmd)
	else:
		rsh_cmd.extend(pipes.quote(x) for x in cmd)

	return rsh_cmd

# list zfs datasets
def zfs_list(dataset, recurse=False, max_depth=None,
		properties=('name',), types=('filesystem',), remote_shell=None):
	# split user and host from remote source
	netloc, dataset = parse_scp_url(dataset)

	cmd = ['zfs', 'list']

	if max_depth is not None:
		cmd.append('-d')
		cmd.append(str(max_depth))
	elif recurse:
		cmd.append('-r')

	cmd.append('-H')
	cmd.append('-o')
	cmd.append(','.join(properties))

	cmd.append('-t')
	cmd.append(','.join(types))

	cmd.append(dataset)

	# prepare command for remote execution
	if netloc:
		user, _, host = netloc.rpartition('@')
		cmd = remote_cmd(cmd, host, username=user, remote_shell=remote_shell)

	# execute command, capturing stdout and stderr
	log.debug(' '.join(cmd))
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = (s.strip() for s in p.communicate())
	returncode = p.wait()

	# raise OSError if dataset not found
	if returncode == 1 and err.endswith('dataset does not exist'):
		raise OSError(errno.ENOENT, err, dataset)

	# raise CalledProcessError for any other error
	if returncode:
		raise subprocess.CalledProcessError(returncode, cmd, output=err)

	# parse list output
	rows = (line.split('\t') for line in out.splitlines())
	datasets = [dict(zip(properties, row)) for row in rows]

	# prepend netloc to remote dataset names
	if netloc and 'name' in properties:
		for d in datasets:
			d['name'] = netloc + ':' + d['name']

	return datasets

# TODO: check fs is mounted:
def zfs_mountpoint(dataset, **kwargs):
	mount_props = zfs_list(dataset, properties=('mountpoint'))[0]
	mountpoint = mount_props['mountpoint']
	if mountpoint == 'none':
		raise Exception('mountpoint not set for ' + dataset)
	return mountpoint

# process backup sets sequentially in the order given
def backup(source, destination, verbose=False, dry_run=False,
		timestamp_format=None, exclude=(), rsync_extra_args=(),
		remote_shell=None):
	# use local rsync command from current path
	rsync_args = ['rsync']

	# set remote shell if specified
	if remote_shell:
		rsync_args.append('--rsh=%s' % (' '.join([pipes.quote(a) for a in remote_shell]), ))

	# add default args for snapshots
# TODO: don't set rsync options unless specified / reduce set of default options?
	snapshot_args = (
		'--quiet', # required to ignore skipped special files
		'-rlptgo', # note: -D causes problems, so expand --archive
		# alt: --archive --no-devices --no-specials
		'--one-file-system',
		'--numeric-ids',
		'--acls', # note: can fail if local and remote users don't match
		'--xattrs', # note: requires rsync 3
		'--inplace', # note: requires rsync 3 on Mac OS X
		'--delete-during',
# TODO: remove this - don't want to try to delete .Trash, .fseventsd, .zfs etc on target
#		'--delete-excluded',
	)
	rsync_args.extend(snapshot_args)

	# add any extra rsync args
	rsync_args.extend(rsync_extra_args)

	# add excluded paths
	rsync_args.extend(('--exclude=%s' % (e,) for e in exclude))

	# set source and destination
	rsync_args.append(source)

	filesystem, snapshot = parse_snapshot(destination)

	host, fs = split_dest(destination)
	rsync_dest = zfs_mountpoint(fs, host=host, ssh_config=ssh_config)
	if host:
		rsync_dest = host + ':' + rsync_dest
	rsync_args.append(rsync_dest)

	log.info('pushing %s to %s', source, destination)
	log.debug(' '.join(rsync_args))
	if not dry_run:
		retcode = call(rsync_args)
		if retcode == 24:
			# Partial transfer due to vanished source files - not a problem
			log.warning('rsync reported partial transfer due to vanished source files')
			pass
		elif retcode != 0:
			log.error('rsync failed with error code %d', retcode)
			sys.exit(retcode)

	# create snapshot
	zfs_args = ['zfs', 'autosnapshot', fs]
	log.info('creating snapshot %s', fs)
	log.debug(' '.join(zfs_args))
	# XXX: will fail if snapshot completes with same timestamp as previous
	if not dry_run:
		check_call(zfs_args, host=host, ssh_config=ssh_config)

def main(argv=sys.argv):
	# set up command-line options
# TODO: allow arbitrary rsync args
# - parser.parse_known_args() handy but doesn't pick up eg -r from -lptrgo
# - parse manually
#   - must check entire list (up to '--')
#   - detect -[...]r[...] or --recursive, and --rsh=...
#   - strip --snapshot-property and --timestamp-format
# - use --rsync-args='-a --xattrs ...'
#   - need to parse rsync args and extract -r, --rsh
# - or require all zfs args first, then --rsync-args arg [...] src [...] dst
#   - only need to split out dst for zfs to get mountpoint, create snapshot etc
#   - not much advantage over prev - still need to find -r
	for arg in argv:
		if True:
			pass
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('-n', '--dry-run', action='store_true')

	# read command-line options, remaining arguments are list of backup sets
	try:
		(args, backupsets) = parser.parse_known_args(argv[1:])
	except SystemExit:
		return 2

	# set up logging
	log_level = max(logging.WARNING - (args.verbose * 10), logging.DEBUG)
	logging.basicConfig(level=log_level)

	source, destination = backupsets

	# start backup
	backup(source, destination, dry_run=args.dry_run,
		exclude=(), rsync_extra_args=())

	return 0

if __name__ == '__main__':
	sys.exit(main())
