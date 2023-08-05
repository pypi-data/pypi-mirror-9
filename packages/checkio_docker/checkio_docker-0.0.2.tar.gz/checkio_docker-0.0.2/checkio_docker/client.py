import json
import logging
import shutil
import tempfile

from io import BytesIO

from docker import Client
from docker.utils import kwargs_from_env

from .parser import MissionFilesHandler


class DockerClient(object):
    PREFIX_IMAGE = 'checkio'

    def __init__(self, name_image, environment, connection_params=None):
        if connection_params is None:
            connection_params = kwargs_from_env(assert_hostname=False)
        self._client = Client(**connection_params)
        self.name_image = "{}/{}-{}".format(self.PREFIX_IMAGE, name_image, environment)
        self.environment = environment
        self._container = None

    def run(self, command, mem_limit=None, cpu_shares=None):
        self.create_container(command, mem_limit, cpu_shares)
        self.start()

    def create_container(self, command, mem_limit=None, cpu_shares=None):
        logging.debug("Create container: {}, {}, {}".format(command, mem_limit, cpu_shares))
        self._container = self._client.create_container(
            image=self.name_image,
            command=command,
            mem_limit=mem_limit,
            cpu_shares=cpu_shares
        )

    def start(self):
        self._client.start(container=self.container_id)

    def stop(self):
        self._client.stop(container=self.container_id, timeout=2)

    def remove_container(self):
        self._client.remove_container(container=self.container_id)

    def logs(self, stream=False, logs=False):
        return self._client.attach(container=self.container_id, stream=stream, logs=logs)

    @property
    def container_id(self):
        return self._container.get('Id')

    def build(self, name_image, path=None, dockerfile_content=None):
        """
        Build new docker image
        :param name_image: name of new docker image
        :param path: path to dir with Dockerfile
        :param dockerfile_content: content of Dockerfile

        Must be passed one of this args: path or dockerfile_content
        :return: None
        """
        logging.debug("Build: {}, {}, {}".format(name_image, path))

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

    def build_mission(self, source_path):
        """
        Build new docker image
        :param path: path to dir with CheckiO mission
        :return: None
        """
        working_path = None
        try:
            working_path = tempfile.mkdtemp()
            mission_source = MissionFilesHandler(self.environment, working_path)
            compiled_path = mission_source.compile_from_files(source_path)
            self.build(name_image=self.name_image, path=compiled_path)
        finally:
            if working_path is not None:
                shutil.rmtree(working_path)

    def build_mission_repo(self, repository):
        """
        Build new docker image
        :param repository: repository of CheckiO mission
        :return: None
        """
        working_path = None
        try:
            working_path = tempfile.mkdtemp()
            mission_source = MissionFilesHandler(self.environment, working_path)
            compiled_path = mission_source.compile_from_git(repository)
            self.build(name_image=self.name_image, path=compiled_path)
        finally:
            if working_path is not None:
                shutil.rmtree(working_path)
