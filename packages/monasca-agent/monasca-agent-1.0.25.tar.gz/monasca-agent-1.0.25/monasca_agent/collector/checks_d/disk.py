import psutil
import logging
import os

log = logging.getLogger(__name__)

import monasca_agent.collector.checks as checks


class Disk(checks.AgentCheck):

    def __init__(self, name, init_config, agent_config):
        super(Disk, self).__init__(name, init_config, agent_config)

    def check(self, instance):
        """Capture disk stats

        """
        dimensions = self._set_dimensions(None, instance)

        if instance is not None:
            use_mount = instance.get("use_mount", True)
            send_io_stats = instance.get("send_io_stats", True)
            # If we filter devices, get the list.
            device_blacklist_re = self._get_re_exclusions(instance)
            fs_types_to_ignore = self._get_fs_exclusions(instance)
        else:
            use_mount = True
            fs_types_to_ignore = []
            device_blacklist_re = None
            send_io_stats = True

        partitions = psutil.disk_partitions(all=True)
        if send_io_stats:
            disk_stats = psutil.disk_io_counters(perdisk=True)
        disk_count = 0
        for partition in partitions:
            if partition.fstype not in fs_types_to_ignore \
                or (device_blacklist_re \
                and not device_blacklist_re.match(partition.device)):
                    device_name = self._get_device_name(partition.device)
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    st = os.statvfs(partition.mountpoint)
                    if use_mount:
                        dimensions.update({'mount_point': partition.mountpoint})
                    self.gauge("disk.space_used_perc",
                               disk_usage.percent,
                               device_name=device_name,
                               dimensions=dimensions)
                    disk_count += 1
                    if st.f_files > 0:
                        self.gauge("disk.inode_used_perc",
                                   round((float(st.f_files - st.f_ffree) / st.f_files) * 100, 2),
                                   device_name=device_name,
                                   dimensions=dimensions)
                        disk_count += 1

                    log.debug('Collected {0} disk usage metrics for partition {1}'.format(disk_count, partition.mountpoint))
                    disk_count = 0
                    if send_io_stats:
                        try:
                            stats = disk_stats[device_name]
                            self.rate("io.read_req_sec", round(float(stats.read_count), 2), device_name=device_name, dimensions=dimensions)
                            self.rate("io.write_req_sec", round(float(stats.write_count), 2), device_name=device_name, dimensions=dimensions)
                            self.rate("io.read_kbytes_sec", round(float(stats.read_bytes / 1024), 2), device_name=device_name, dimensions=dimensions)
                            self.rate("io.write_kbytes_sec", round(float(stats.write_bytes / 1024), 2), device_name=device_name, dimensions=dimensions)
                            self.rate("io.read_time_sec", round(float(stats.read_time / 1000), 2), device_name=device_name, dimensions=dimensions)
                            self.rate("io.write_time_sec", round(float(stats.write_time / 1000), 2), device_name=device_name, dimensions=dimensions)

                            log.debug('Collected 6 disk I/O metrics for partition {0}'.format(partition.mountpoint))
                        except KeyError:
                            log.debug('No Disk I/O metrics available for {0}...Skipping'.format(device_name))

    def _get_re_exclusions(self, instance):
        """Parse device blacklist regular expression"""
        filter = None
        try:
            filter_device_re = instance.get('device_blacklist_re', None)
            if filter_device_re:
                filter = re.compile(filter_device_re)
        except re.error as err:
            log.error('Error processing regular expression {0}'.format(filter_device_re))

        return filter

    def _get_fs_exclusions(self, instance):
        """parse comma separated file system types to ignore list"""
        file_system_list = []
        try:
            file_systems = instance.get('ignore_filesystem_types', None)
            if file_systems:
                # Parse file system types
                file_system_list.extend([x.strip() for x in file_systems.split(',')])
        except ValueError:
            log.info("Unable to process ignore_filesystem_types.")

        return file_system_list

    def _get_device_name(self, device):
        start = device.rfind("/")
        if start > -1:
            device_name = device[start + 1:]
        else:
            device_name = device

        return device_name
