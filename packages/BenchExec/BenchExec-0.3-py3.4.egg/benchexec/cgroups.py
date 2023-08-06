"""
BenchExec is a framework for reliable benchmarking.
This file is part of BenchExec.

Copyright (C) 2007-2015  Dirk Beyer
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# prepare for Python 3
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import shutil
import signal
import tempfile
import time

from . import util as util

__all__ = [
           'find_my_cgroups',
           'CPUACCT',
           'CPUSET',
           'FREEZER',
           'MEMORY',
           ]

CGROUP_NAME_PREFIX='benchmark_'

CPUACCT = 'cpuacct'
CPUSET = 'cpuset'
FREEZER = 'freezer'
MEMORY = 'memory'
ALL_KNOWN_SUBSYSTEMS = set([CPUACCT, CPUSET, FREEZER, MEMORY])


def find_my_cgroups():
    """
    Return a Cgroup object with the cgroups of the current process.
    Note that it is not guaranteed that all subsystems are available
    in the returned object, as a subsystem may not be mounted.
    Check with "subsystem in <instance>" before using.
    A subsystem may also be present but we do not have the rights to create
    child cgroups, this can be checked with require_subsystem().
    """
    logging.debug('Analyzing /proc/mounts and /proc/self/cgroup for determining cgroups.')
    my_cgroups = dict(_find_own_cgroups())

    cgroupsParents = {}
    for subsystem, mount in _find_cgroup_mounts():
        cgroupsParents[subsystem] = os.path.join(mount, my_cgroups[subsystem])

    return Cgroup(cgroupsParents)


def _find_cgroup_mounts():
    """
    Return the information which subsystems are mounted where.
    @return a generator of tuples (subsystem, mountpoint)
    """
    try:
        with open('/proc/mounts', 'rt') as mountsFile:
            for mount in mountsFile:
                mount = mount.split(' ')
                if mount[2] == 'cgroup':
                    mountpoint = mount[1]
                    options = mount[3]
                    for option in options.split(','):
                        if option in ALL_KNOWN_SUBSYSTEMS:
                            yield (option, mountpoint)
    except IOError:
        logging.exception('Cannot read /proc/mounts')


def _find_own_cgroups():
    """
    For all subsystems, return the information in which (sub-)cgroup this process is in.
    (Each process is in exactly cgroup in each hierarchy.)
    @return a generator of tuples (subsystem, cgroup)
    """
    try:
        with open('/proc/self/cgroup', 'rt') as ownCgroupsFile:
            for ownCgroup in ownCgroupsFile:
                #each line is "id:subsystem,subsystem:path"
                ownCgroup = ownCgroup.strip().split(':')
                path = ownCgroup[2][1:] # remove leading /
                for subsystem in ownCgroup[1].split(','):
                    yield (subsystem, path)
    except IOError:
        logging.exception('Cannot read /proc/self/cgroup')



def kill_all_tasks_in_cgroup(cgroup):
    tasksFile = os.path.join(cgroup, 'tasks')
    freezer_file = os.path.join(cgroup, 'freezer.state')

    def try_write_to_freezer(content):
        try:
            util.write_file(content, freezer_file)
        except IOError:
            pass # expected if freezer not enabled, we try killing without it

    i = 0
    while True:
        i += 1
        for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGKILL]:
            try_write_to_freezer('FROZEN')
            with open(tasksFile, 'rt') as tasks:
                task = None
                for task in tasks:
                    task = task.strip()
                    if i > 1:
                        logging.warning('Run has left-over process with pid {0} in cgroup {1}, sending signal {2} (try {3}).'.format(task, cgroup, sig, i))
                    util.kill_process(int(task), sig)

                if task is None:
                    return # No process was hanging, exit
            try_write_to_freezer('THAWED')
            time.sleep(i * 0.5) # wait for the process to exit, this might take some time


def remove_cgroup(cgroup):
    if not os.path.exists(cgroup):
        logging.warning('Cannot remove CGroup {0}, because it does not exist.'.format(cgroup))
        return
    assert os.path.getsize(os.path.join(cgroup, 'tasks')) == 0
    try:
        os.rmdir(cgroup)
    except OSError:
        # sometimes this fails because the cgroup is still busy, we try again once
        try:
            os.rmdir(cgroup)
        except OSError as e:
            logging.warning("Failed to remove cgroup {0}: error {1} ({2})"
                            .format(cgroup, e.errno, e.strerror))


class Cgroup(object):
    def __init__(self, cgroupsPerSubsystem):
        assert cgroupsPerSubsystem.keys() <= ALL_KNOWN_SUBSYSTEMS
        assert all(cgroupsPerSubsystem.values())
        self.per_subsystem = cgroupsPerSubsystem # update self.paths on every update to this
        self.paths = set(cgroupsPerSubsystem.values()) # without duplicates

    def __contains__(self, key):
        return key in self.per_subsystem

    def __getitem__(self, key):
        return self.per_subsystem[key]

    def __str__(self):
        return str(self.paths)

    def require_subsystem(self, subsystem):
        """
        Check whether the given subsystem is enabled and is writable
        (i.e., new cgroups can be created for it).
        Produces a log message for the user if one of the conditions is not fulfilled.
        If the subsystem is enabled but not writable, it will be removed from
        this instance such that further checks with "in" will return "False".
        @return A boolean value.
        """
        if not subsystem in self:
            logging.warning('Cgroup subsystem {0} is not enabled. Please enable it with "sudo mount -t cgroup none /sys/fs/cgroup".'.format(subsystem))
            return False

        try:
            test_cgroup = self.create_fresh_child_cgroup(subsystem)
            test_cgroup.remove()
        except OSError as e:
            self.paths = set(self.per_subsystem.values())
            logging.warning('Cannot use cgroup hierarchy mounted at {0} for subsystem {1}, reason: {2}. If permissions are wrong, please run "sudo chmod o+wt \'{0}\'".'.format(self.per_subsystem[subsystem], subsystem, e.strerror))
            del self.per_subsystem[subsystem]
            return False

        return True

    def create_fresh_child_cgroup(self, *subsystems):
        """
        Create child cgroups of the current cgroup for at least the given subsystems.
        @return: A Cgroup instance representing the new child cgroup(s). 
        """
        assert set(subsystems).issubset(self.per_subsystem.keys())
        createdCgroupsPerSubsystem = {}
        createdCgroupsPerParent = {}
        for subsystem in subsystems:
            parentCgroup = self.per_subsystem[subsystem]
            if parentCgroup in createdCgroupsPerParent:
                # reuse already created cgroup
                createdCgroupsPerSubsystem[subsystem] = createdCgroupsPerParent[parentCgroup]
                continue

            cgroup = tempfile.mkdtemp(prefix=CGROUP_NAME_PREFIX, dir=parentCgroup)
            createdCgroupsPerSubsystem[subsystem] = cgroup
            createdCgroupsPerParent[parentCgroup] = cgroup

            # add allowed cpus and memory to cgroup if necessary
            # (otherwise we can't add any tasks)
            def copy_parent_to_child(name):
                shutil.copyfile(os.path.join(parentCgroup, name), os.path.join(cgroup, name))
            try:
                copy_parent_to_child('cpuset.cpus')
                copy_parent_to_child('cpuset.mems')
            except IOError:
                # expected to fail if cpuset subsystem is not enabled in this hierarchy
                pass

        return Cgroup(createdCgroupsPerSubsystem)

    def add_task(self, pid):
        """
        Add a process to the cgroups represented by this instance.
        """
        for cgroup in self.paths:
            with open(os.path.join(cgroup, 'tasks'), 'w') as tasksFile:
                tasksFile.write(str(pid))

    def kill_all_tasks(self):
        """
        Kill all tasks in this cgroup forcefully.
        """
        for cgroup in self.paths:
            kill_all_tasks_in_cgroup(cgroup)

    def kill_all_tasks_recursively(self):
        """
        Kill all tasks in this cgroup and all its children cgroups forcefully.
        Additionally, the children cgroups will be deleted.
        """
        def kill_all_tasks_in_cgroup_recursively(cgroup):
            files = [os.path.join(cgroup,f) for f in os.listdir(cgroup)]
            subdirs = filter(os.path.isdir, files)

            for subCgroup in subdirs:
                kill_all_tasks_in_cgroup_recursively(subCgroup)
                remove_cgroup(subCgroup)

            kill_all_tasks_in_cgroup(cgroup)

        for cgroup in self.paths:
            kill_all_tasks_in_cgroup_recursively(cgroup)

    def has_value(self, subsystem, option):
        """
        Check whether the given value exists in the given subsystem.
        Does not make a difference whether the value is readable, writable, or both.
        Do not include the subsystem name in the option name.
        Only call this method if the given subsystem is available.  
        """
        assert subsystem in self
        return os.path.isfile(os.path.join(self.per_subsystem[subsystem], subsystem + '.' + option))

    def get_value(self, subsystem, option):
        """
        Read the given value from the given subsystem.
        Do not include the subsystem name in the option name.
        Only call this method if the given subsystem is available.  
        """
        assert subsystem in self
        return util.read_file(self.per_subsystem[subsystem], subsystem + '.' + option)

    def get_file_lines(self, subsystem, option):
        """
        Read the lines of the given file from the given subsystem.
        Do not include the subsystem name in the option name.
        Only call this method if the given subsystem is available.
        """
        assert subsystem in self
        with open(os.path.join(self.per_subsystem[subsystem], subsystem + '.' + option)) as f:
            for line in f:
                yield line

    def get_key_value_pairs(self, subsystem, filename):
        """
        Read the lines of the given file from the given subsystem
        and split the lines into key-value pairs.
        Do not include the subsystem name in the option name.
        Only call this method if the given subsystem is available.
        """
        assert subsystem in self
        return util.read_key_value_pairs_from_file(self.per_subsystem[subsystem], subsystem + '.' + filename)

    def set_value(self, subsystem, option, value):
        """
        Write the given value for the given subsystem.
        Do not include the subsystem name in the option name.
        Only call this method if the given subsystem is available.  
        """
        assert subsystem in self
        util.write_file(str(value), self.per_subsystem[subsystem], subsystem + '.' + option)

    def remove(self):
        """
        Remove all cgroups this instance represents from the system.
        This instance is afterwards not usable anymore!
        """
        for cgroup in self.paths:
            remove_cgroup(cgroup)

        del self.paths
        del self.per_subsystem

    def read_cputime(self):
        """
        Read the cputime usage of this cgroup. CPUACCT cgroup needs to be available.
        @return cputime usage in seconds
        """
        return float(self.get_value(CPUACCT, 'usage'))/1000000000 # nano-seconds to seconds

    def read_allowed_memory_banks(self):
        """Get the list of all memory banks allowed by this cgroup."""
        return util.parse_int_list(self.get_value(CPUSET, 'mems'))
