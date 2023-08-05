oar-docker CHANGELOG
====================


version 0.4.1
=============

Released on Jan 28th 2015

- Cleaned up unversionned OAR files (git clean) from sources before installing OAR (Fixed #20)


version 0.4.0
=============

Released on Jan 24th 2015

- Python3 support
- Prefixed all container outputs with the container hostname  (like oardocker logs subcommand)
- Added ``--force-rm`` and ``--pull`` options to oardocker build subcommand
- Allowed user to build custom images with custom_setup.sh script located in ``.oardocker/images/<image_name>/``
- Added a proper way to shutdown container
- Updated /etc/hosts when reseting containers
- Removed dockerpty package from dependencies
- Removed oardocker ssh/ssh-config subcommand
- Added ``--verbose`` option
- Fixed oardocker logs subcommand


version 0.3.2
=============

Released on Dec 16th 2014

- Added ``--enable-x11`` option to allow containers to display x11 applications
- Auto-loaded OAR module on python startup
- Added ``--env`` option to ``oardocker start`` to set custom environment variables
- Added ``--workdir`` option to ``oardocker exec``

version 0.3.1
=============

Released on Nov 27th 2014

**Bug fixes**:
- Fixed the Dockerfiles "FROM" statement

**Improvements**:
- Removed implicit 'default' alias from available env


version 0.3.0
=============

Released on Nov 27th 2014

**Features**:

- Added ``oardocker exec`` command
- Manage multiple environment variants with ``oardocker init``: added wheezy|jessie|python bases images

**Bug fixes**:
- Revert default environment to Debian Wheezy due to breaking OAR API in Jessie
- Fixed locales issue

**Improvements**:
- better synchronisation between oar-server and postgresql services


version 0.2.0
=============

Released on Nov 5th 2014

**Features**:

- Updated base images to debian jessie
- Added ``oardocker connect`` to connect to the nodes without ssh
- The commands ``oardocker ssh`` and ``oardocker ssh-config`` are deprecated from now

**Improvements**:

- Removed supervisor and make init process less complex by only using my_init.d statup scripts
- Customized help parameter to accept ``-h`` and ``--help``
- Used docker client binary for some task instead of the API

**Bug fixes**:

- Make sure that /etc/hosts file contain the localhost entry

version 0.1.4
=============

Released on Oct 28th 2014

- Ignored my-init scripts if filename ends by "~"
- Added wait_pgsql script to wait postgresql to be available
- Fixed monika config (db server hostname is server)
- Removed old code
- Adapt cgroup mount script to job_resource_manager_cgroup.pl and remove old cpuset workaround
- Fixed cpu/core/thread affinity


version 0.1.3
=============

Released on Sep 10th 2014

- Added `oar reset` cmd to restart containers
- Added a better comments about oardocker images with git information
- Used default job_resource_manager script (from oar sources)
- Mount the host cgroup path in the containers (default path is /sys/fs/cgroup)
- Removed stopped containers from ssh_config
- Remove dnsmasq and mount a custom /etc/hosts for the nodes (need docker >= 1.2.0)


version 0.1.2
=============

Released on Sep 16th 2014

- Keep compatible with older versions of git
- Don't name the containers
- Mounting OAR src as Copy-on-Write directory with unionfs-fuse
- Stopped installation when container failed during ``oardocker install``
- Added option to print version
- Allow ssh connection with different user

version 0.1.1
=============

Released on Sep 11th 2014

 - Minor bug fixes

version 0.1
===========

Released on Sep 11th 2014

Initial public release of oar-docker
