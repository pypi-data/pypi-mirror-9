# Rekall Memory Forensics
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
@author:       Andrew Case
@license:      GNU General Public License 2.0 or later
@contact:      atcuno@gmail.com
@organization: Digital Forensics Solutions
"""

from rekall import testlib
from rekall.plugins import core
from rekall.plugins.linux import common


class ProcMaps(common.LinProcessFilter):
    """Gathers process maps for linux."""

    __name = "maps"

    def render(self, renderer):
        renderer.table_header([("Pid", "pid", "8"),
                               ("Start", "start", "[addrpad]"),
                               ("End", "end", "[addrpad]"),
                               ("Flags", "flags", "6"),
                               ("Pgoff", "pgoff", "[addrpad]"),
                               ("Major", "major", "6"),
                               ("Minor", "minor", "6"),
                               ("Inode", "inode", "13"),
                               ("File Path", "file_path", "80"),
                               ])

        for task in self.filter_processes():
            if not task.mm:
                continue

            for vma in task.mm.mmap.walk_list("vm_next"):
                if vma.vm_file:
                    inode = vma.vm_file.dentry.d_inode
                    major, minor = inode.i_sb.major, inode.i_sb.minor
                    ino = inode.i_ino
                    pgoff = vma.vm_pgoff << 12
                    fname = task.get_path(vma.vm_file)
                else:
                    (major, minor, ino, pgoff) = [0] * 4

                    if (vma.vm_start <= task.mm.start_brk and
                        vma.vm_end >= task.mm.brk):
                        fname = "[heap]"
                    elif (vma.vm_start <= task.mm.start_stack and
                          vma.vm_end >= task.mm.start_stack):
                        fname = "[stack]"
                    else:
                        fname = ""

                renderer.table_row(task.pid,
                                   vma.vm_start,
                                   vma.vm_end,
                                   vma.vm_flags,
                                   pgoff,
                                   major,
                                   minor,
                                   ino,
                                   fname)


class TestProcMaps(testlib.SimpleTestCase):
    PARAMETERS = dict(
        commandline="maps --proc_regex %(proc_name)s",
        proc_name="bash"
        )


class LinVadDump(core.DirectoryDumperMixin, common.LinProcessFilter):
    """Dump the VMA memory for a process."""

    __name = "vaddump"

    def render(self, renderer):
        for task in self.filter_processes():
            if not task.mm:
                continue

            renderer.format("Pid: {0:6}\n", task.pid)

            # Get the task and all process specific information
            task_space = task.get_process_address_space()
            name = task.comm

            for vma in task.mm.mmap.walk_list("vm_next"):
                if not vma.vm_file:
                    continue

                filename = "{0}.{1}.{2:08x}-{3:08x}.dmp".format(
                    name, task.pid, vma.vm_start, vma.vm_end)

                renderer.format(u"Writing {0}, pid {1} to {2}\n",
                                task.comm, task.pid, filename)

                with renderer.open(directory=self.dump_dir,
                                   filename=filename,
                                   mode='wb') as fd:
                    self.CopyToFile(task_space, vma.vm_start, vma.vm_end, fd)


class TestLinVadDump(common.LinuxTestMixin, testlib.HashChecker):
    PARAMETERS = dict(
        commandline="vaddump --proc_regex %(proc_name)s --dump_dir %(tempdir)s",
        proc_name="bash"
        )
