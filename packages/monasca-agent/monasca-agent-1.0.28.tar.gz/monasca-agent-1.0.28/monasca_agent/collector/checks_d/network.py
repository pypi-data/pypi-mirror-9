# stdlib
import logging
import re
import psutil

# project
import monasca_agent.collector.checks as checks

log = logging.getLogger(__name__)


class Network(checks.AgentCheck):

    def __init__(self, name, init_config, agent_config):
        super(Network, self).__init__(name, init_config, agent_config)

    def check(self, instance):
        """Capture network metrics

        """
        dimensions = self._set_dimensions(None, instance)

        excluded_ifaces = instance.get('excluded_interfaces', [])
        if excluded_ifaces:
            log.debug('Excluding network devices: {0}'.format(excluded_ifaces))

        exclude_re = instance.get('excluded_interface_re', None)
        if exclude_re:
            exclude_iface_re = re.compile(exclude_re)
            log.debug('Excluding network devices matching: {0}'.format(exclude_re))
        else:
            exclude_iface_re = None

        nics = psutil.net_io_counters(pernic=True)
        count = 0
        for nic_name in nics.keys():
            if nic_name not in excluded_ifaces or exclude_iface_re and not exclude_iface_re.match(nic_name):
                nic = nics[nic_name]
                self.rate('net.in_bytes_sec', nic.bytes_recv, device_name=nic_name, dimensions=dimensions)
                self.rate('net.out_bytes_sec', nic.bytes_sent, device_name=nic_name, dimensions=dimensions)
                self.rate('net.in_packets_sec', nic.packets_recv, device_name=nic_name, dimensions=dimensions)
                self.rate('net.out_packets_sec', nic.packets_sent, device_name=nic_name, dimensions=dimensions)
                self.rate('net.in_errors_sec', nic.errin, device_name=nic_name, dimensions=dimensions)
                self.rate('net.out_errors_sec', nic.errout, device_name=nic_name, dimensions=dimensions)
                self.rate('net.in_packets_dropped_sec', nic.dropin, device_name=nic_name, dimensions=dimensions)
                self.rate('net.out_packets_dropped_sec', nic.dropout, device_name=nic_name, dimensions=dimensions)

                log.debug('Collected 8 network metrics for device {0}'.format(nic_name))
