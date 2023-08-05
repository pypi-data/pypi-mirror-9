import re
import urllib2

from monasca_agent.collector.checks import AgentCheck
from monasca_agent.collector.checks.utils import add_basic_auth
from monasca_agent.common.util import headers


class Nginx(AgentCheck):

    """Tracks basic nginx metrics via the status module

    * number of connections
    * number of requets per second

    Requires nginx to have the status option compiled.
    See http://wiki.nginx.org/HttpStubStatusModule for more details

    $ curl http://localhost:81/nginx_status/
    Active connections: 8
    server accepts handled requests
     1156958 1156958 4491319
    Reading: 0 Writing: 2 Waiting: 6
    """

    def check(self, instance):
        if 'nginx_status_url' not in instance:
            raise Exception('NginX instance missing "nginx_status_url" value.')
        dimensions = instance.get('dimensions', {})

        response = self._get_data(instance)
        self._get_metrics(response, dimensions)

    def _get_data(self, instance):
        url = instance.get('nginx_status_url')
        req = urllib2.Request(url, None, headers(self.agent_config))
        if 'user' in instance and 'password' in instance:
            add_basic_auth(req, instance['user'], instance['password'])
        request = urllib2.urlopen(req)
        return request.read()

    def _get_metrics(self, response, dimensions):
        # Thanks to http://hostingfu.com/files/nginx/nginxstats.py for this code
        # Connections
        parsed = re.search(r'Active connections:\s+(\d+)', response)
        if parsed:
            connections = int(parsed.group(1))
            self.gauge("nginx.net.connections", connections, dimensions=dimensions)

        # Requests per second
        parsed = re.search(r'\s*(\d+)\s+(\d+)\s+(\d+)', response)
        if parsed:
            conn = int(parsed.group(1))
            requests = int(parsed.group(3))
            self.rate("nginx.net.conn_opened_per_s", conn, dimensions=dimensions)
            self.rate("nginx.net.request_per_s", requests, dimensions=dimensions)

        # Connection states, reading, writing or waiting for clients
        parsed = re.search(r'Reading: (\d+)\s+Writing: (\d+)\s+Waiting: (\d+)', response)
        if parsed:
            reading, writing, waiting = map(int, parsed.groups())
            self.gauge("nginx.net.reading", reading, dimensions=dimensions)
            self.gauge("nginx.net.writing", writing, dimensions=dimensions)
            self.gauge("nginx.net.waiting", waiting, dimensions=dimensions)

    @staticmethod
    def parse_agent_config(agentConfig):
        instances = []

        # Try loading from the very old format
        nginx_url = agentConfig.get("nginx_status_url", None)
        if nginx_url is not None:
            instances.append({
                'nginx_status_url': nginx_url
            })

        # Try the older multi-instance style
        # nginx_status_url_1: http://www.example.com/nginx_status:first_tag
        # nginx_status_url_2: http://www.example2.com/nginx_status:8080:second_tag
        # nginx_status_url_2: http://www.example3.com/nginx_status:third_tag
        def load_conf(index=1):
            instance = agentConfig.get("nginx_status_url_%s" % index, None)
            if instance is not None:
                instance = instance.split(":")
                instances.append({
                    'nginx_status_url': ":".join(instance[:-1]),
                    'dimensions': {'instance': instance[-1]}
                })
                load_conf(index + 1)

        load_conf()

        if not instances:
            return False

        return {
            'instances': instances
        }
