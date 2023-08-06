import json
import logging

from io import BytesIO

from docker import Client
from docker.utils import kwargs_from_env

from .container import Container
from .parser import MissionFilesCompiler
from .utils import TemporaryDirectory


class DockerClient(object):
    PREFIX_IMAGE = 'checkio'
    LINUX_SOCKET = 'unix://var/run/docker.sock'

    def __init__(self, connection_params=None):
        if connection_params is None:
            connection_params = kwargs_from_env(assert_hostname=False)
            if 'base_url' not in connection_params:
                connection_params['base_url'] = self.LINUX_SOCKET
        self._client = Client(**connection_params)

    def __getattr__(self, attr):
        return getattr(self._client, attr)

    def get_image_name(self, mission):
        return "{}/{}".format(self.PREFIX_IMAGE, mission)

    def run(self, mission, command, mem_limit=None, cpu_shares=None):
        container = self.create_container(mission, command, mem_limit, cpu_shares)
        container.start()
        return container

    def create_container(self, mission, command, name=None, mem_limit=None, cpu_shares=None):
        logging.debug("Create container: {}, {}, {}".format(command, mem_limit, cpu_shares))
        image_name = self.get_image_name(mission)
        container = self._client.create_container(
            image=image_name,
            command=command,
            name=name,
            mem_limit=mem_limit,
            cpu_shares=cpu_shares
        )
        return Container(container=container, connection=self._client)

    def build(self, name_image, path=None, dockerfile_content=None):
        """
        Build new docker image
        :param name_image: name of new docker image
        :param path: path to dir with Dockerfile
        :param dockerfile_content: content of Dockerfile

        Must be passed one of this args: path or dockerfile_content
        :return: None
        """
        logging.debug("Build: {}, {}".format(name_image, path))

        def _format_output_line(line):
            line_str = line.decode().strip()
            data = json.loads(line_str)
            for key, value in data.items():
                # TODO: if any error - raise exception
                if isinstance(value, basestring):
                    value = value.strip()
                if not value:
                    return None
                return "{}: {}".format(key, value)

        file_obj = None
        if dockerfile_content is not None:
            file_obj = BytesIO(dockerfile_content.encode('utf-8'))
        for line in self._client.build(path=path, fileobj=file_obj, tag=name_image, nocache=True):
            line = _format_output_line(line)
            if line is not None:
                logging.info(line)

    def build_mission(self, mission, repository=None, source_path=None, compiled_path=None):
        """
        Build new docker image
        :param mission: mission slug
        :param repository: repository of CheckiO mission
        :param compiled_path: path for store compiled mission
        :return:
        """
        assert repository or source_path

        image_name = self.get_image_name(mission)
        with TemporaryDirectory() as temp_path:
            if compiled_path is None:
                compiled_path = temp_path

            mission_source = MissionFilesCompiler(compiled_path)
            mission_source.compile(source_path=source_path, repository=repository)
            self.build(name_image=image_name, path=mission_source.path_verification)
