Sluice
======
Sluice is a set of tools for managing ZFS snapshots:

* ``zfs-autosnapshot`` creates snapshots with automatically-generated names

* ``zfs-copy`` combines ``zfs send`` and ``zfs receive``

* ``zfs-sync`` does one-way synchronisation of snapshots between two datasets

with several others on the way:

* ``zfs-cull``

* ``zfs-import``

* ``zfs-export``

Motivation / rationale
----------------------
(combine with description?)

- goals:

  - unix philosophy

    - snapshot, sync and cull can quite happily be independent operations with separate schedules

  - avoid config file

    - since tools are split up, fewer command-line options are required

    - schedule with cron/launchd and configure targets as args

    - can also use zfs user props for config

  - no requirement for remote installation (provided by weir)

Installation
------------
Requires Python 2.7.

To install Sluice, simply:

``$ pip install sluice``

Usage
-----
...

License
-------
Licensed under the Common Development and Distribution License (CDDL).
