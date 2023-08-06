import uuid

import six
import yaml

from .transformer import BaseTransformer


class ComposeTransformer(BaseTransformer):
    """
    A transformer for docker-compose

    To use this class:

    .. code-block:: python

        transformer = ComposeTransformer('./docker-compose.yml')
        normalized_keys = transformer.ingest_containers()

    """

    def _read_stream(self, stream):
        return yaml.safe_load(stream=stream)

    def ingest_containers(self, containers=None):
        """
        Transform the YAML into a dict with normalized keys
        """
        containers = containers or self.stream or {}

        output_containers = []

        for container_name, definition in six.iteritems(containers):
            container = definition.copy()
            container['name'] = container_name
            output_containers.append(container)

        return output_containers

    @staticmethod
    def emit_containers(containers, verbose=True):

        output = {}
        for container in containers:
            name_in_container = container.get('name')
            if not name_in_container:
                name = str(uuid.uuid4())
            else:
                name = container.pop('name')
            output[name] = container

        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True
        return yaml.dump(
            output,
            default_flow_style=False,
            Dumper=noalias_dumper
        )

    @staticmethod
    def validate(container):

        return container

    @staticmethod
    def _parse_port_mapping(mapping):
        parts = str(mapping).split(':')
        if len(parts) == 1:
            return {
                'container_port': int(parts[0])
            }
        if len(parts) == 2 and '.' not in mapping:
            return {
                'host_port': int(parts[0]),
                'container_port': int(parts[1])
            }
        if len(parts) == 3:
            if '.' in parts[0]:
                return {
                    'host_ip': parts[0],
                    'host_port': int(parts[1]),
                    'container_port': int(parts[2])
                }
            else:
                return {
                    'host_port': int(parts[0]),
                    'container_ip': parts[1],
                    'container_port': int(parts[2])
                }
        if len(parts) == 4:
            return {
                'host_ip': parts[0],
                'host_port': int(parts[1]),
                'container_ip': parts[2],
                'container_port': int(parts[3])
            }

    @staticmethod
    def ingest_port_mappings(port_mappings):
        """
        Transform the docker-compose port mappings to base schema port_mappings

        :param port_mappings: The compose port mappings
        :type port_mappings: list
        :return: the base schema port_mappings
        :rtype: list of dict
        """
        return [ComposeTransformer._parse_port_mapping(mapping) for mapping in port_mappings]

    @staticmethod
    def _emit_mapping(mapping):
        parts = []
        if mapping.get('host_ip'):
            parts.append(str(mapping['host_ip']))
        if mapping.get('host_port'):
            parts.append(str(mapping['host_port']))
        if mapping.get('container_ip'):
            parts.append(str(mapping['container_ip']))
        if mapping.get('container_port'):
            parts.append(str(mapping['container_port']))
        return ':'.join(parts)

    @staticmethod
    def emit_port_mappings(port_mappings):
        """
        :param port_mappings: the base schema port_mappings
        :type port_mappings: list of dict
        :return:
        :rtype: list of str
        """
        return [str(ComposeTransformer._emit_mapping(mapping)) for mapping in port_mappings]

    @staticmethod
    def ingest_memory(memory):
        """
        Transform the memory into bytes

        :param memory: Compose memory definition. (1g, 24k)
        :type memory: str
        :return: The memory in bytes
        :rtype: int
        """
        def lshift(num, shift):
            return num << shift

        def rshift(num, shift):
            return num >> shift

        bit_shift = {
            'g': {'func': lshift, 'shift': 30},
            'm': {'func': lshift, 'shift': 20},
            'k': {'func': lshift, 'shift': 10},
            'b': {'func': rshift, 'shift': 0}
        }
        unit = memory[-1]
        number = int(memory[:-1])
        return bit_shift[unit]['func'](number, bit_shift[unit]['shift'])

    @staticmethod
    def emit_memory(memory):
        return '{}b'.format(memory)

    @staticmethod
    def ingest_cpu(cpu):
        return cpu

    @staticmethod
    def emit_cpu(cpu):
        return cpu

    @staticmethod
    def ingest_environment(environment):
        output = {}
        if type(environment) is list:
            for kv in environment:
                index = kv.find('=')
                output[str(kv[:index])] = str(kv[index + 1:])
        if type(environment) is dict:
            for key, value in six.iteritems(environment):
                output[str(key)] = str(value)
        return output

    @staticmethod
    def emit_environment(environment):
        return environment

    @staticmethod
    def ingest_command(command):
        return command

    @staticmethod
    def emit_command(command):
        return command

    @staticmethod
    def ingest_entrypoint(entrypoint):
        return entrypoint

    @staticmethod
    def emit_entrypoint(entrypoint):
        return entrypoint

    @staticmethod
    def ingest_volumes_from(volumes_from):
        return volumes_from

    @staticmethod
    def emit_volumes_from(volumes_from):
        return volumes_from
