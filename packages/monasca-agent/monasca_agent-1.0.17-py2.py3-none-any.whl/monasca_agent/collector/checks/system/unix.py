"""Unix system checks.
"""

# stdlib
import functools
import logging
import operator
import platform
import re
import subprocess as sp
import sys
import time

# project

import monasca_agent.collector.checks.check as check
import monasca_agent.common.metrics as metrics
import monasca_agent.common.util as util


# locale-resilient float converter
to_float = lambda s: float(s.replace(",", "."))


class Disk(check.Check):

    """Collects metrics about the machine's disks.
    """

    def check(self):
        """Get disk space/inode stats.
        """
        fs_types_to_ignore = []
        # First get the configuration.
        if self.agent_config is not None:
            use_mount = self.agent_config.get("use_mount", False)
            blacklist_re = self.agent_config.get('device_blacklist_re', None)
            for fs_type in self.agent_config.get('ignore_filesystem_types', []):
                fs_types_to_ignore.extend(['-x', fs_type])
        else:
            use_mount = False
            blacklist_re = None
        platform_name = sys.platform

        try:
            dfk_out = _get_subprocess_output(['df', '-k'] + fs_types_to_ignore)
            stats = self.parse_df_output(
                dfk_out,
                platform_name,
                use_mount=use_mount,
                blacklist_re=blacklist_re
            )

            # Collect inode metrics.
            dfi_out = _get_subprocess_output(['df', '-i'] + fs_types_to_ignore)
            inodes = self.parse_df_output(
                dfi_out,
                platform_name,
                inodes=True,
                use_mount=use_mount,
                blacklist_re=blacklist_re
            )
            # parse into a list of Measurements
            stats.update(inodes)
            timestamp = time.time()
            measurements = [metrics.Measurement(key.split('.', 1)[1],
                                                timestamp,
                                                value,
                                                self._set_dimensions({'device': key.split('.', 1)[0]}),
                                                None)
                            for key, value in stats.iteritems()]

            return measurements

        except Exception:
            self.logger.exception('Error collecting disk stats')
            return []

    def parse_df_output(
            self, df_output, platform_name, inodes=False, use_mount=False, blacklist_re=None):
        """Parse the output of the df command.

        If use_volume is true the volume is used to anchor the metric, otherwise false the mount
        point is used. Returns a tuple of (disk, inode).
        """
        usage_data = {}

        # Transform the raw output into tuples of the df data.
        devices = self._transform_df_output(df_output, blacklist_re)

        # If we want to use the mount point, replace the volume name on each line.
        for parts in devices:
            try:
                if use_mount:
                    parts[0] = parts[-1]
                if inodes:
                    if util.Platform.is_darwin(platform_name):
                        # Filesystem 512-blocks Used Available Capacity iused ifree %iused  Mounted
                        # Inodes are in position 5, 6 and we need to compute the total
                        # Total
                        parts[1] = int(parts[5]) + int(parts[6])  # Total
                        parts[2] = int(parts[5])  # Used
                        parts[3] = int(parts[6])  # Available
                    elif util.Platform.is_freebsd(platform_name):
                        # Filesystem 1K-blocks Used Avail Capacity iused ifree %iused Mounted
                        # Inodes are in position 5, 6 and we need to compute the total
                        parts[1] = int(parts[5]) + int(parts[6])  # Total
                        parts[2] = int(parts[5])  # Used
                        parts[3] = int(parts[6])  # Available
                    else:
                        parts[1] = int(parts[1])  # Total
                        parts[2] = int(parts[2])  # Used
                        parts[3] = int(parts[3])  # Available
                else:
                    parts[1] = int(parts[1])  # Total
                    parts[2] = int(parts[2])  # Used
                    parts[3] = int(parts[3])  # Available
            except IndexError:
                self.logger.exception("Cannot parse %s" % (parts,))

            # Some partitions (EFI boot) may appear to have 0 available inodes
            if parts[1] == 0:
                continue

            #
            # Remote shared storage device names like '10.103.0.220:/instances'
            # cause invalid metrics on the api server side, so if we encounter
            # a colon, remove everything to the left of it (including the
            # offending colon).
            #
            device_name = parts[0]
            idx = device_name.find(":")
            if idx > 0:
                device_name = device_name[(idx+1):]
            if inodes:
                usage_data['%s.disk.inode_used_perc' % device_name] = float(parts[2]) / parts[1] * 100
            else:
                usage_data['%s.disk.space_used_perc' % device_name] = float(parts[2]) / parts[1] * 100

        return usage_data

    @staticmethod
    def _is_number(a_string):
        try:
            float(a_string)
        except ValueError:
            return False
        return True

    def _is_real_device(self, device):
        """Return true if we should track the given device name and false otherwise.
        """
        # First, skip empty lines.
        if not device or len(device) <= 1:
            return False

        # Filter out fake devices.
        device_name = device[0]
        if device_name == 'none':
            return False

        # Now filter our fake hosts like 'map -hosts'. For example:
        #       Filesystem    1024-blocks     Used Available Capacity  Mounted on
        #       /dev/disk0s2    244277768 88767396 155254372    37%    /
        #       map -hosts              0        0         0   100%    /net
        blocks = device[1]
        if not self._is_number(blocks):
            return False
        return True

    def _flatten_devices(self, devices):
        # Some volumes are stored on their own line. Rejoin them here.
        previous = None
        for parts in devices:
            if len(parts) == 1:
                previous = parts[0]
            elif previous and self._is_number(parts[0]):
                # collate with previous line
                parts.insert(0, previous)
                previous = None
            else:
                previous = None
        return devices

    def _transform_df_output(self, df_output, blacklist_re):
        """Given raw output for the df command, transform it into a normalized list devices.

        A 'device' is a list with fields corresponding to the output of df output on each platform.
        """
        all_devices = [l.strip().split() for l in df_output.split("\n")]

        # Skip the header row and empty lines.
        raw_devices = [l for l in all_devices[1:] if l]

        # Flatten the disks that appear in the mulitple lines.
        flattened_devices = self._flatten_devices(raw_devices)

        # Filter fake disks.
        def keep_device(device):
            if not self._is_real_device(device):
                return False
            if blacklist_re and blacklist_re.match(device[0]):
                return False
            return True

        devices = filter(keep_device, flattened_devices)

        return devices


class IO(check.Check):

    def __init__(self, logger, agent_config=None):
        super(IO, self).__init__(logger, agent_config)
        self.header_re = re.compile(r'([%\\/\-_a-zA-Z0-9]+)[\s+]?')
        self.item_re = re.compile(r'^([a-zA-Z0-9\/]+)')
        self.value_re = re.compile(r'\d+\.\d+')
        self.stat_blacklist = ["await", "wrqm/s", "avgqu-sz", "r_await", "w_await", "rrqm/s",
                               "avgrq-sz", "%util", "svctm"]

    def _parse_linux2(self, output):
        recent_stats = output.split('Device:')[2].split('\n')
        header = recent_stats[0]
        header_names = re.findall(self.header_re, header)

        io_stats = {}

        for statsIndex in range(1, len(recent_stats)):
            row = recent_stats[statsIndex]

            if not row:
                # Ignore blank lines.
                continue

            device_match = self.item_re.match(row)

            if device_match is not None:
                # Sometimes device names span two lines.
                device = device_match.groups()[0]
            else:
                continue

            values = re.findall(self.value_re, row)

            if not values:
                # Sometimes values are on the next line so we encounter
                # instances of [].
                continue

            io_stats[device] = {}

            for header_index in range(len(header_names)):
                header_name = header_names[header_index]
                io_stats[device][self.xlate(header_name, "linux")] = values[header_index]

        return io_stats

    @staticmethod
    def _parse_darwin(output):
        lines = [l.split() for l in output.split("\n") if len(l) > 0]
        disks = lines[0]
        lastline = lines[-1]
        io = {}
        for idx, disk in enumerate(disks):
            kb_t, tps, mb_s = map(float, lastline[(3 * idx):(3 * idx) + 3])  # 3 cols at a time
            io[disk] = {
                'system.io.bytes_per_s': mb_s * 10 ** 6,
            }
        return io

    @staticmethod
    def xlate(metric_name, os_name):
        """Standardize on linux metric names.
        """
        if os_name == "sunos":
            names = {"wait": "await",
                     "svc_t": "svctm",
                     "%b": "%util",
                     "kr/s": "io.read_kbytes_sec",
                     "kw/s": "io.write_kbytes_sec",
                     "actv": "avgqu-sz"}
        elif os_name == "freebsd":
            names = {"svc_t": "await",
                     "%b": "%util",
                     "kr/s": "io.read_kbytes_sec",
                     "kw/s": "io.write_kbytes_sec",
                     "wait": "avgqu-sz"}
        elif os_name == "linux":
            names = {"rkB/s": "io.read_kbytes_sec",
                     "r/s": "io.read_req_sec",
                     "wkB/s": "io.write_kbytes_sec",
                     "w/s": "io.write_req_sec"}
        # translate if possible
        return names.get(metric_name, metric_name)

    def check(self):
        """Capture io stats.

        @rtype dict
        @return [metrics.Measurement, ]
        """
        io = {}
        try:
            if util.Platform.is_linux():
                stdout = sp.Popen(['iostat', '-d', '1', '2', '-x', '-k'],
                                  stdout=sp.PIPE,
                                  close_fds=True).communicate()[0]

                #                 Linux 2.6.32-343-ec2 (ip-10-35-95-10)   12/11/2012      _x86_64_        (2 CPU)
                #
                # Device:     rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await  svctm  %util
                # sda1          0.00    17.61    0.26   32.63     4.23   201.04    12.48     0.16    4.81   0.53   1.73
                # sdb           0.00     2.68    0.19    3.84     5.79    26.07    15.82     0.02    4.93   0.22   0.09
                # sdg           0.00     0.13    2.29    3.84   100.53    30.61    42.78     0.05    8.41   0.88   0.54
                # sdf           0.00     0.13    2.30    3.84   100.54    30.61    42.78     0.06    9.12   0.90   0.55
                # md0           0.00     0.00    0.05    3.37     1.41    30.01    18.35     0.00    0.00   0.00   0.00
                #
                # Device:     rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await  svctm  %util
                # sda1          0.00     0.00    0.00   10.89     0.00    43.56     8.00     0.03    2.73   2.73   2.97
                # sdb           0.00     0.00    0.00    2.97     0.00    11.88     8.00     0.00    0.00   0.00   0.00
                # sdg           0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00   0.00   0.00
                # sdf           0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00   0.00   0.00
                # md0           0.00     0.00    0.00    0.00     0.00     0.00     0.00
                # 0.00    0.00   0.00   0.00
                io.update(self._parse_linux2(stdout))

            elif sys.platform == "sunos5":
                iostat = sp.Popen(["iostat", "-x", "-d", "1", "2"],
                                  stdout=sp.PIPE,
                                  close_fds=True).communicate()[0]

                #                   extended device statistics <-- since boot
                # device      r/s    w/s   kr/s   kw/s wait actv  svc_t  %w  %b
                # ramdisk1    0.0    0.0    0.1    0.1  0.0  0.0    0.0   0   0
                # sd0         0.0    0.0    0.0    0.0  0.0  0.0    0.0   0   0
                # sd1        79.9  149.9 1237.6 6737.9  0.0  0.5    2.3   0  11
                #                   extended device statistics <-- past second
                # device      r/s    w/s   kr/s   kw/s wait actv  svc_t  %w  %b
                # ramdisk1    0.0    0.0    0.0    0.0  0.0  0.0    0.0   0   0
                # sd0         0.0    0.0    0.0    0.0  0.0  0.0    0.0   0   0
                # sd1         0.0  139.0    0.0 1850.6  0.0  0.0    0.1   0   1

                # discard the first half of the display (stats since boot)
                lines = [l for l in iostat.split("\n") if len(l) > 0]
                lines = lines[len(lines) / 2:]

                assert "extended device statistics" in lines[0]
                headers = lines[1].split()
                assert "device" in headers
                for l in lines[2:]:
                    cols = l.split()
                    # cols[0] is the device
                    # cols[1:] are the values
                    io[cols[0]] = {}
                    for i in range(1, len(cols)):
                        io[cols[0]][self.xlate(headers[i], "sunos")] = cols[i]

            elif sys.platform.startswith("freebsd"):
                iostat = sp.Popen(["iostat", "-x", "-d", "1", "2"],
                                  stdout=sp.PIPE,
                                  close_fds=True).communicate()[0]

                # Be careful!
                # It looks like SunOS, but some columms (wait, svc_t) have different meaning
                #                        extended device statistics
                # device     r/s   w/s    kr/s    kw/s wait svc_t  %b
                # ad0        3.1   1.3    49.9    18.8    0   0.7   0
                #                         extended device statistics
                # device     r/s   w/s    kr/s    kw/s wait svc_t  %b
                # ad0        0.0   2.0     0.0    31.8    0   0.2   0

                # discard the first half of the display (stats since boot)
                lines = [l for l in iostat.split("\n") if len(l) > 0]
                lines = lines[len(lines) / 2:]

                assert "extended device statistics" in lines[0]
                headers = lines[1].split()
                assert "device" in headers
                for l in lines[2:]:
                    cols = l.split()
                    # cols[0] is the device
                    # cols[1:] are the values
                    io[cols[0]] = {}
                    for i in range(1, len(cols)):
                        io[cols[0]][self.xlate(headers[i], "freebsd")] = cols[i]
            elif sys.platform == 'darwin':
                iostat = sp.Popen(['iostat', '-d', '-c', '2', '-w', '1'],
                                  stdout=sp.PIPE,
                                  close_fds=True).communicate()[0]
                #          disk0           disk1          <-- number of disks
                #    KB/t tps  MB/s     KB/t tps  MB/s
                #   21.11  23  0.47    20.01   0  0.00
                #    6.67   3  0.02     0.00   0  0.00    <-- line of interest
                io = self._parse_darwin(iostat)
            else:
                return []

            # If we filter devices, do it know.
            if self.agent_config is not None:
                device_blacklist_re = self.agent_config.get('device_blacklist_re', None)
            else:
                device_blacklist_re = None
            if device_blacklist_re:
                filtered_io = {}
                for device, stats in io.iteritems():
                    if not device_blacklist_re.match(device):
                        filtered_io[device] = stats
            else:
                filtered_io = io

            measurements = []
            timestamp = time.time()
            for dev_name, stats in filtered_io.iteritems():
                filtered_stats = {stat: stats[stat]
                                  for stat in stats.iterkeys() if stat not in self.stat_blacklist}
                m_list = [metrics.Measurement(key,
                                              timestamp,
                                              value,
                                              self._set_dimensions({'device': dev_name}),
                                              None)
                          for key, value in filtered_stats.iteritems()]
                measurements.extend(m_list)

            return measurements

        except Exception:
            self.logger.exception("Cannot extract IO statistics")
            return []


class Load(check.Check):

    def check(self):
        if util.Platform.is_linux():
            try:
                loadAvrgProc = open('/proc/loadavg', 'r')
                uptime = loadAvrgProc.readlines()
                loadAvrgProc.close()
            except Exception:
                self.logger.exception('Cannot extract load')
                return []

            uptime = uptime[0]  # readlines() provides a list but we want a string

        elif sys.platform in ('darwin', 'sunos5') or sys.platform.startswith("freebsd"):
            # Get output from uptime
            try:
                uptime = sp.Popen(['uptime'],
                                  stdout=sp.PIPE,
                                  close_fds=True).communicate()[0]
            except Exception:
                self.logger.exception('Cannot extract load')
                return {}

        # Split out the 3 load average values
        load = [res.replace(',', '.') for res in re.findall(r'([0-9]+[\.,]\d+)', uptime)]
        timestamp = time.time()
        dimensions = self._set_dimensions(None)

        return [metrics.Measurement('load.avg_1_min', timestamp, float(load[0]), dimensions),
                metrics.Measurement('load.avg_5_min', timestamp, float(load[1]), dimensions),
                metrics.Measurement('load.avg_15_min', timestamp, float(load[2]), dimensions)]


class Memory(check.Check):

    def __init__(self, logger, agent_config=None):
        super(Memory, self).__init__(logger, agent_config)
        macV = None
        if sys.platform == 'darwin':
            macV = platform.mac_ver()
            macV_minor_version = int(re.match(r'10\.(\d+)\.?.*', macV[0]).group(1))

        # Output from top is slightly modified on OS X 10.6 (case #28239) and greater
        if macV and (macV_minor_version >= 6):
            self.topIndex = 6
        else:
            self.topIndex = 5

        self.pagesize = 0
        if sys.platform == 'sunos5':
            try:
                pgsz = sp.Popen(['pagesize'],
                                stdout=sp.PIPE,
                                close_fds=True).communicate()[0]
                self.pagesize = int(pgsz.strip())
            except Exception:
                # No page size available
                pass

    def check(self):
        memData = {}

        if util.Platform.is_linux():
            try:
                meminfoProc = open('/proc/meminfo', 'r')
                lines = meminfoProc.readlines()
                meminfoProc.close()
            except Exception:
                self.logger.exception('Cannot get memory metrics from /proc/meminfo')
                return []

            # $ cat /proc/meminfo
            # MemTotal:        7995360 kB
            # MemFree:         1045120 kB
            # Buffers:          226284 kB
            # Cached:           775516 kB
            # SwapCached:       248868 kB
            # Active:          1004816 kB
            # Inactive:        1011948 kB
            # Active(anon):     455152 kB
            # Inactive(anon):   584664 kB
            # Active(file):     549664 kB
            # Inactive(file):   427284 kB
            # Unevictable:     4392476 kB
            # Mlocked:         4392476 kB
            # SwapTotal:      11120632 kB
            # SwapFree:       10555044 kB
            # Dirty:              2948 kB
            # Writeback:             0 kB
            # AnonPages:       5203560 kB
            # Mapped:            50520 kB
            # Shmem:             10108 kB
            # Slab:             161300 kB
            # SReclaimable:     136108 kB
            # SUnreclaim:        25192 kB
            # KernelStack:        3160 kB
            # PageTables:        26776 kB
            # NFS_Unstable:          0 kB
            # Bounce:                0 kB
            # WritebackTmp:          0 kB
            # CommitLimit:    15118312 kB
            # Committed_AS:    6703508 kB
            # VmallocTotal:   34359738367 kB
            # VmallocUsed:      400668 kB
            # VmallocChunk:   34359329524 kB
            # HardwareCorrupted:     0 kB
            # HugePages_Total:       0
            # HugePages_Free:        0
            # HugePages_Rsvd:        0
            # HugePages_Surp:        0
            # Hugepagesize:       2048 kB
            # DirectMap4k:       10112 kB
            # DirectMap2M:     8243200 kB

            # We run this several times so one-time compile now
            regexp = re.compile(r'^(\w+):\s+([0-9]+)')
            meminfo = {}

            for line in lines:
                try:
                    match = re.search(regexp, line)
                    if match is not None:
                        meminfo[match.group(1)] = match.group(2)
                except Exception:
                    self.logger.exception("Cannot parse /proc/meminfo")

            # Physical memory
            # FIXME units are in MB, we should use bytes instead
            try:
                memData['mem.total_mb'] = int(meminfo.get('MemTotal', 0)) / 1024
                memData['mem.free_mb'] = int(meminfo.get('MemFree', 0)) / 1024
                memData['mem.used_buffers'] = int(meminfo.get('Buffers', 0)) / 1024
                memData['mem.used_cached'] = int(meminfo.get('Cached', 0)) / 1024
                memData['mem.used_shared'] = int(meminfo.get('Shmem', 0)) / 1024

                # Usable is relative since cached and buffers are actually used to speed things up.
                memData['mem.usable_mb'] = memData['mem.free_mb'] + \
                    memData['mem.used_buffers'] + memData['mem.used_cached']

                if memData['mem.total_mb'] > 0:
                    memData['mem.usable_perc'] = float(
                        (memData['mem.usable_mb']) / float(memData['mem.total_mb']) * 100)
            except Exception:
                self.logger.exception('Cannot compute stats from /proc/meminfo')

            # Swap
            # FIXME units are in MB, we should use bytes instead
            try:
                memData['mem.swap_total_mb'] = int(meminfo.get('SwapTotal', 0)) / 1024
                memData['mem.swap_free_mb'] = int(meminfo.get('SwapFree', 0)) / 1024

                memData['mem.swap_used_mb'] = memData[
                    'mem.swap_total_mb'] - memData['mem.swap_free_mb']

                if memData['mem.swap_total_mb'] > 0:
                    memData['mem.swap_free_perc'] = float(
                        (memData['mem.swap_free_mb']) / float(memData['mem.swap_total_mb']) * 100)
            except Exception:
                self.logger.exception('Cannot compute swap stats')
                return []
        elif sys.platform == 'darwin':
            macV = platform.mac_ver()
            macV_minor_version = int(re.match(r'10\.(\d+)\.?.*', macV[0]).group(1))

            try:
                top = sp.Popen(['top', '-l 1'], stdout=sp.PIPE, close_fds=True).communicate()[0]
                sysctl = sp.Popen(
                    ['sysctl', 'vm.swapusage'], stdout=sp.PIPE, close_fds=True).communicate()[0]
            except Exception:
                self.logger.exception('getMemoryUsage')
                return []

            # Deal with top
            lines = top.split('\n')
            physParts = re.findall(r'([0-9]\d+)', lines[self.topIndex])

            # Deal with sysctl
            swapParts = re.findall(r'([0-9]+\.\d+)', sysctl)

            # Mavericks changes the layout of physical memory format in `top`
            physUsedPartIndex = 3
            physFreePartIndex = 4
            if macV and (macV_minor_version >= 9):
                physUsedPartIndex = 0
                physFreePartIndex = 2

            memData = {'physUsed': physParts[physUsedPartIndex],
                       'physFree': physParts[physFreePartIndex],
                       'swapUsed': swapParts[1],
                       'swapFree': swapParts[2]}

        elif sys.platform.startswith("freebsd"):
            try:
                sysctl = sp.Popen(
                    ['sysctl', 'vm.stats.vm'], stdout=sp.PIPE, close_fds=True).communicate()[0]
            except Exception:
                self.logger.exception('getMemoryUsage')
                return []

            lines = sysctl.split('\n')

            # ...
            # vm.stats.vm.v_page_size: 4096
            # vm.stats.vm.v_page_count: 759884
            # vm.stats.vm.v_wire_count: 122726
            # vm.stats.vm.v_active_count: 109350
            # vm.stats.vm.v_cache_count: 17437
            # vm.stats.vm.v_inactive_count: 479673
            # vm.stats.vm.v_free_count: 30542
            # ...

            # We run this several times so one-time compile now
            regexp = re.compile(r'^vm\.stats\.vm\.(\w+):\s+([0-9]+)')
            meminfo = {}

            for line in lines:
                try:
                    match = re.search(regexp, line)
                    if match is not None:
                        meminfo[match.group(1)] = match.group(2)
                except Exception:
                    self.logger.exception("Cannot parse sysctl vm.stats.vm output")

            # Physical memory
            try:
                pageSize = int(meminfo.get('v_page_size'))

                memData['physTotal'] = (int(meminfo.get('v_page_count', 0))
                                        * pageSize) / 1048576
                memData['physFree'] = (int(meminfo.get('v_free_count', 0))
                                       * pageSize) / 1048576
                memData['physCached'] = (int(meminfo.get('v_cache_count', 0))
                                         * pageSize) / 1048576
                memData['physUsed'] = ((int(meminfo.get('v_active_count'), 0) +
                                        int(meminfo.get('v_wire_count', 0)))
                                       * pageSize) / 1048576
                memData['physUsable'] = ((int(meminfo.get('v_free_count'), 0) +
                                          int(meminfo.get('v_cache_count', 0)) +
                                          int(meminfo.get('v_inactive_count', 0))) *
                                         pageSize) / 1048576

                if memData['physTotal'] > 0:
                    memData['physPctUsable'] = float(
                        memData['physUsable']) / float(memData['physTotal'])
            except Exception:
                self.logger.exception('Cannot compute stats from /proc/meminfo')

            # Swap
            try:
                sysctl = sp.Popen(
                    ['swapinfo', '-m'], stdout=sp.PIPE, close_fds=True).communicate()[0]
            except Exception:
                self.logger.exception('getMemoryUsage')
                return []

            lines = sysctl.split('\n')

            # ...
            # Device          1M-blocks     Used    Avail Capacity
            # /dev/ad0s1b           570        0      570     0%
            # ...

            assert "Device" in lines[0]

            try:
                memData['swapTotal'] = 0
                memData['swapFree'] = 0
                memData['swapUsed'] = 0
                for line in lines[1:-1]:
                    line = line.split()
                    memData['swapTotal'] += int(line[1])
                    memData['swapFree'] += int(line[3])
                    memData['swapUsed'] += int(line[2])
            except Exception:
                self.logger.exception('Cannot compute stats from swapinfo')
                return []
        elif sys.platform == 'sunos5':
            try:
                memData = {}
                kmem = sp.Popen(["kstat", "-c", "zone_memory_cap", "-p"],
                                stdout=sp.PIPE,
                                close_fds=True).communicate()[0]

                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:anon_alloc_fail   0
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:anonpgin  0
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:class     zone_memory_cap
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:crtime    16359935.0680834
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:execpgin  185
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:fspgin    2556
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:n_pf_throttle     0
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:n_pf_throttle_usec        0
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:nover     0
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:pagedout  0
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:pgpgin    2741
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:physcap   536870912  <--
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:rss       115544064  <--
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:snaptime  16787393.9439095
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:swap      91828224   <--
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:swapcap   1073741824 <--
                # memory_cap:360:53aa9b7e-48ba-4152-a52b-a6368c:zonename
                # 53aa9b7e-48ba-4152-a52b-a6368c3d9e7c

                # turn memory_cap:360:zone_name:key value
                # into { "key": value, ...}
                kv = [l.strip().split() for l in kmem.split("\n") if len(l) > 0]
                entries = dict([(k.split(":")[-1], v) for (k, v) in kv])
                # extract rss, physcap, swap, swapcap, turn into MB
                convert = lambda v: int(long(v)) / 2 ** 20
                memData["physTotal"] = convert(entries["physcap"])
                memData["physUsed"] = convert(entries["rss"])
                memData["physFree"] = memData["physTotal"] - memData["physUsed"]
                memData["swapTotal"] = convert(entries["swapcap"])
                memData["swapUsed"] = convert(entries["swap"])
                memData["swapFree"] = memData["swapTotal"] - memData["swapUsed"]

                if memData['swapTotal'] > 0:
                    memData['swapPctFree'] = float(
                        memData['swapFree']) / float(memData['swapTotal'])
            except Exception:
                self.logger.exception("Cannot compute mem stats from kstat -c zone_memory_cap")
                return []

        timestamp = time.time()
        dimensions = self._set_dimensions(None)
        return [metrics.Measurement(key, timestamp, value, dimensions) for key, value in memData.iteritems()]


class Cpu(check.Check):

    def check(self):
        """Return an aggregate of CPU stats across all CPUs.

        When figures are not available, False is sent back.
        """

        if util.Platform.is_linux():
            mpstat = sp.Popen(['mpstat', '1', '3'], stdout=sp.PIPE, close_fds=True).communicate()[0]
            # topdog@ip:~$ mpstat 1 3
            # Linux 2.6.32-341-ec2 (ip)   01/19/2012  _x86_64_  (2 CPU)
            #
            # 04:22:41 PM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest   %idle
            # 04:22:42 PM  all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
            # 04:22:43 PM  all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
            # 04:22:44 PM  all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
            # Average:     all    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00  100.00
            #
            # OR
            #
            # Thanks to Mart Visser to spotting this one.
            # blah:/etc/dd-agent# mpstat
            # Linux 2.6.26-2-xen-amd64 (atira)  02/17/2012  _x86_64_
            #
            # 05:27:03 PM  CPU    %user   %nice   %sys %iowait    %irq   %soft  %steal  %idle   intr/s
            # 05:27:03 PM  all    3.59    0.00    0.68    0.69    0.00   0.00    0.01   95.03    43.65
            #
            lines = mpstat.split("\n")
            legend = [l for l in lines if "%usr" in l or "%user" in l]
            avg = [l for l in lines if "Average" in l]
            if len(legend) == 1 and len(avg) == 1:
                headers = [h for h in legend[0].split() if h not in ("AM", "PM")]
                data = avg[0].split()

                # Userland
                # Debian lenny says %user so we look for both
                # One of them will be 0
                cpu_metrics = {"%usr": None, "%user": None, "%nice": None,
                               "%iowait": None, "%idle": None, "%sys": None,
                               "%irq": None, "%soft": None, "%steal": None}

                for cpu_m in cpu_metrics:
                    cpu_metrics[cpu_m] = self._get_value(headers, data, cpu_m, filter_value=110)

                if any([v is None for v in cpu_metrics.values()]):
                    self.logger.warning("Invalid mpstat data: %s" % data)

                cpu_user = cpu_metrics["%usr"] + cpu_metrics["%user"] + cpu_metrics["%nice"]
                cpu_system = cpu_metrics["%sys"] + cpu_metrics["%irq"] + cpu_metrics["%soft"]
                cpu_wait = cpu_metrics["%iowait"]
                cpu_idle = cpu_metrics["%idle"]
                cpu_stolen = cpu_metrics["%steal"]

                return self._format_results(cpu_user,
                                            cpu_system,
                                            cpu_wait,
                                            cpu_idle,
                                            cpu_stolen)
            else:
                return []

        elif sys.platform == 'darwin':
            # generate 3 seconds of data
            # ['          disk0           disk1       cpu     load average', '    KB/t tps  MB/s     KB/t tps  MB/s  us sy id   1m   5m   15m', '   21.23  13  0.27    17.85   7  0.13  14  7 79  1.04 1.27 1.31', '    4.00   3  0.01     5.00   8  0.04  12 10 78  1.04 1.27 1.31', '']
            iostats = sp.Popen(['iostat',
                                '-C',
                                '-w',
                                '3',
                                '-c',
                                '2'],
                               stdout=sp.PIPE,
                               close_fds=True).communicate()[0]
            lines = [l for l in iostats.split("\n") if len(l) > 0]
            legend = [l for l in lines if "us" in l]
            if len(legend) == 1:
                headers = legend[0].split()
                data = lines[-1].split()
                cpu_user = self._get_value(headers, data, "us")
                cpu_sys = self._get_value(headers, data, "sy")
                cpu_wait = 0
                cpu_idle = self._get_value(headers, data, "id")
                cpu_st = 0
                return self._format_results(cpu_user, cpu_sys, cpu_wait, cpu_idle, cpu_st)
            else:
                self.logger.warn(
                    "Expected to get at least 4 lines of data from iostat instead of just " +
                    str(
                        iostats[
                            : max(
                                80,
                                len(iostats))]))
                return []

        elif sys.platform.startswith("freebsd"):
            # generate 3 seconds of data
            # tty            ada0              cd0            pass0             cpu
            # tin  tout  KB/t tps  MB/s   KB/t tps  MB/s   KB/t tps  MB/s  us ni sy in id
            # 0    69 26.71   0  0.01   0.00   0  0.00   0.00   0  0.00   2  0  0  1 97
            # 0    78  0.00   0  0.00   0.00   0  0.00   0.00   0  0.00   0  0  0  0 100
            iostats = sp.Popen(
                ['iostat', '-w', '3', '-c', '2'], stdout=sp.PIPE, close_fds=True).communicate()[0]
            lines = [l for l in iostats.split("\n") if len(l) > 0]
            legend = [l for l in lines if "us" in l]
            if len(legend) == 1:
                headers = legend[0].split()
                data = lines[-1].split()
                cpu_user = self._get_value(headers, data, "us")
                cpu_nice = self._get_value(headers, data, "ni")
                cpu_sys = self._get_value(headers, data, "sy")
                cpu_intr = self._get_value(headers, data, "in")
                cpu_wait = 0
                cpu_idle = self._get_value(headers, data, "id")
                cpu_stol = 0
                return self._format_results(cpu_user + cpu_nice, cpu_sys + cpu_intr, cpu_wait, cpu_idle, cpu_stol)

            else:
                self.logger.warn(
                    "Expected to get at least 4 lines of data from iostat instead of just " +
                    str(
                        iostats[
                            :max(
                                80,
                                len(iostats))]))
                return []

        elif sys.platform == 'sunos5':
            # mpstat -aq 1 2
            # SET minf mjf xcal  intr ithr  csw icsw migr smtx  srw syscl  usr sys  wt idl sze
            # 0 5239   0 12857 22969 5523 14628   73  546 4055    1 146856    5   6   0  89  24 <-- since boot
            # 1 ...
            # SET minf mjf xcal  intr ithr  csw icsw migr smtx  srw syscl  usr sys  wt idl sze
            # 0 20374   0 45634 57792 5786 26767   80  876 20036    2 724475   13  13   0  75  24 <-- past 1s
            # 1 ...
            # http://docs.oracle.com/cd/E23824_01/html/821-1462/mpstat-1m.html
            #
            # Will aggregate over all processor sets
            try:
                mpstat = sp.Popen(
                    ['mpstat', '-aq', '1', '2'], stdout=sp.PIPE, close_fds=True).communicate()[0]
                lines = [l for l in mpstat.split("\n") if len(l) > 0]
                # discard the first len(lines)/2 lines
                lines = lines[len(lines) / 2:]
                legend = [l for l in lines if "SET" in l]
                assert len(legend) == 1
                if len(legend) == 1:
                    headers = legend[0].split()
                    # collect stats for each processor set
                    # and aggregate them based on the relative set size
                    d_lines = [l for l in lines if "SET" not in l]
                    user = [self._get_value(headers, l.split(), "usr") for l in d_lines]
                    kern = [self._get_value(headers, l.split(), "sys") for l in d_lines]
                    wait = [self._get_value(headers, l.split(), "wt") for l in d_lines]
                    idle = [self._get_value(headers, l.split(), "idl") for l in d_lines]
                    size = [self._get_value(headers, l.split(), "sze") for l in d_lines]
                    count = sum(size)
                    rel_size = [s / count for s in size]
                    dot = lambda v1, v2: functools.reduce(operator.add, map(operator.mul, v1, v2))
                    return self._format_results(dot(user, rel_size),
                                                dot(kern, rel_size),
                                                dot(wait, rel_size),
                                                dot(idle, rel_size),
                                                0.0)
            except Exception:
                self.logger.exception("Cannot compute CPU stats")
                return []
        else:
            self.logger.warn("CPUStats: unsupported platform")
            return []

    def _format_results(self, us, sy, wa, idle, st):
        data = {'cpu.user_perc': us,
                'cpu.system_perc': sy,
                'cpu.wait_perc': wa,
                'cpu.idle_perc': idle,
                'cpu.stolen_perc': st}
        for key in data.keys():
            if data[key] is None:
                del data[key]

        timestamp = time.time()
        dimensions = self._set_dimensions(None)
        return [metrics.Measurement(key, timestamp, value, dimensions) for key, value in data.iteritems()]

    def _get_value(self, legend, data, name, filter_value=None):
        """Using the legend and a metric name, get the value or None from the data line.
        """
        if name in legend:
            value = to_float(data[legend.index(name)])
            if filter_value is not None:
                if value > filter_value:
                    return None
            return value

        else:
            # FIXME return a float or False, would trigger type error if not python
            self.logger.debug("Cannot extract cpu value %s from %s (%s)" % (name, data, legend))
            return 0.0


def _get_subprocess_output(command):
    """Run the given subprocess command and return it's output.

    Raise an Exception if an error occurs.
    """
    proc = sp.Popen(command, stdout=sp.PIPE, close_fds=True)
    return proc.stdout.read()


if __name__ == '__main__':
    # 1s loop with results

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s')
    log = logging.getLogger()
    config = {"device_blacklist_re": re.compile('.*disk0.*')}
    cpu = Cpu(log, config)
    disk = Disk(log, config)
    io = IO(log, config)
    load = Load(log, config)
    mem = Memory(log, config)

    while True:
        print("=" * 10)
        print("--- IO ---")
        print(io.check())
        print("--- Disk ---")
        print(disk.check())
        print("--- CPU ---")
        print(cpu.check())
        print("--- Load ---")
        print(load.check())
        print("--- Memory ---")
        print(mem.check())
        print("\n\n\n")
        time.sleep(1)
