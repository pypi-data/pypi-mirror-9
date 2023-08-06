from unittest import TestCase

from mock import patch
import uuid

from container_transform.fig import FigTransformer


class FigTransformerTests(TestCase):

    def setUp(self):
        self.file_name = './container_transform/tests/fig.yml'
        self.transformer = FigTransformer(self.file_name)

    @patch.object(uuid, 'uuid4', return_value='2e9c3538-b9d3-4f47-8a23-2a19315b370b')
    def test_emit_containers_no_name(self, mock_uuid):
        """
        Test .emit_containers() for a container without a name
        """
        containers = [{
            'image': 'postgres:9.3',
            'cpu': 200
        }]

        output = self.transformer.emit_containers(containers)

        self.assertEqual(
            (
                '{mock_uuid}:\n'
                '  cpu: 200\n'
                '  image: postgres:9.3\n'
            ).format(mock_uuid=mock_uuid.return_value),
            output
        )

    def test_emit_mapping(self):
        """
        Test ._emit_mapping()
        """
        mappping = {
            'host_ip': '192.168.59.103',
            'host_port': 8000,
            'container_ip': '127.0.0.1',
            'container_port': 80,
        }

        self.assertEqual(
            self.transformer._emit_mapping(mappping),
            '192.168.59.103:8000:127.0.0.1:80'
        )

    def test_emit_mapping_missing_ports(self):
        """
        Test ._emit_mapping() missing ports
        """
        mapping = {
            'host_ip': '192.168.59.103',
            'container_ip': '127.0.0.1',
        }

        self.assertEqual(
            self.transformer._emit_mapping(mapping),
            '192.168.59.103:127.0.0.1'
        )

    def test_parse_port_mapping_fails(self):
        """
        Test ._parse_port_mapping() fails on > 4 parts
        """
        mapping = '192.168.59.103:8000:127.0.0.1:80:'

        self.assertEqual(
            self.transformer._parse_port_mapping(mapping),
            None
        )

    def test_ingest_cpu(self):
        cpu = 100
        self.assertEqual(
            self.transformer.ingest_cpu(cpu),
            cpu
        )

    def test_emit_cpu(self):
        cpu = 100
        self.assertEqual(
            self.transformer.emit_cpu(cpu),
            cpu
        )
