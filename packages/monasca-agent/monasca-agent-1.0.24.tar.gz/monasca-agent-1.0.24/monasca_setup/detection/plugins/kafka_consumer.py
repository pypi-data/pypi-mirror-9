import logging
import re
from subprocess import CalledProcessError

from monasca_setup.detection import Plugin, find_process_cmdline, watch_process
from monasca_setup.detection.utils import find_addr_listening_on_port
from monasca_setup.detection.utils import check_output
from monasca_setup import agent_config

log = logging.getLogger(__name__)


class Kafka(Plugin):

    """Detect Kafka daemons and sets up configuration to monitor them.
        This plugin configures the kafka_consumer plugin and does not configure any jmx based checks against kafka.
        Note this plugin will pull the same information from kafka on each node in the cluster it runs on.
        For more information see:
            - https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol
            -
    """

    def __init__(self, template_dir, overwrite=True, alarms=None, port=9092):
        Plugin.__init__(self, template_dir, overwrite, alarms)
        self.port = port
        self.zk_url = self._find_zookeeper_url()
        self.config = agent_config.Plugins()

    def _detect(self):
        """Run detection, set self.available True if the service is detected."""
        if find_process_cmdline('kafka') is not None:
            self.available = True

    def _detect_consumers(self):
        """ Using zookeeper and a kafka connection find the consumers, associated topics and partitions.
        """
        try:
            # The kafka api provides no way to discover existing consumer groups so a query to
            # zookeeper must be made. This is unfortunately fragile as kafka is moving away from
            # zookeeper. Tested with kafka 0.8.1.1
            from kafka.client import KafkaClient
            kafka_connect_str = self._find_kafka_connection()
            kafka = KafkaClient(kafka_connect_str)

            # {'consumer_group_name': { 'topic1': [ 0, 1, 2] # partitions }}
            consumers = {}
            # Find consumers and topics
            for consumer in self._ls_zookeeper('/consumers'):
                consumers[consumer] = dict((topic, kafka.topic_partitions[topic])
                                       for topic in self._ls_zookeeper('/consumers/%s/offsets' % consumer))

            log.info("\tInstalling kafka_consumer plugin.")
            self.config['kafka_consumer'] = {'init_config': None,
                                             'instances': [{'kafka_connect_str': kafka_connect_str,
                                                            'full_output': True,
                                                            'consumer_groups': dict(consumers)}]}
        except Exception:
            log.error('Error Detecting Kafka consumers/topics/partitions')

    def _find_kafka_connection(self):
        listen_ip = find_addr_listening_on_port(self.port)
        if listen_ip:
            log.info("\tKafka found listening on {:s}:{:d}".format(listen_ip, self.port))
        else:
            log.info("\tKafka not found listening on a specific IP (port {:d}), using 'localhost'".format(self.port))
            listen_ip = 'localhost'

        return "{:s}:{:d}".format(listen_ip, self.port)

    @staticmethod
    def _find_zookeeper_url():
        """ Pull the zookeeper url the kafka config.
        :return: Zookeeper url
        """
        zk_connect = re.compile('zookeeper.connect=(.*)')
        try:
            with open('/etc/kafka/server.properties') as settings:
                match = zk_connect.search(settings.read())
        except IOError:
            return None

        if match is None:
            log.error('No zookeeper url found in the kafka server properties.')
            return None

        return match.group(1).split(',')[0]  # Only use the first zk url

    def _ls_zookeeper(self, path):
        """ Do a ls on the given zookeeper path.
            I am using the local command line kafka rather than kazoo because it doesn't make sense to
            have kazoo as a dependency only for detection.
        """
        zk_shell = ['/opt/kafka/bin/zookeeper-shell.sh', self.zk_url, 'ls', path]
        try:
            output = check_output(zk_shell)
        except CalledProcessError:
            log.error('Error running the zookeeper shell to list path %s' % path)
            raise

        # The last line is like '[item1, item2, item3]'
        return [entry.strip() for entry in output.splitlines()[-1].strip('[]').split(',')]

    def build_config(self):
        """Build the config as a Plugins object and return.
            Config includes: consumer_groups (include topics) and kafka_connection_str
        """
        # First watch the process
        self.config.merge(watch_process(['kafka.Kafka'], exact_match=False))
        log.info("\tWatching the kafka process.")

        if self.dependencies_installed() and self.zk_url is not None:
            self._detect_consumers()
        else:
            log.warning("Dependencies not installed, skipping plugin configuration.")
        return self.config

    def dependencies_installed(self):
        try:
            import kafka
        except ImportError:
            return False

        return True
