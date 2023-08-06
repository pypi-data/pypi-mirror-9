import os
import git
import shutil
import tempfile
from distutils.dir_util import copy_tree


class MissionFilesException(Exception):
    pass


class MissionFilesHandler(object):

    DIR_VERIFICATION = 'verification'

    SCHEMA_FILENAME = 'schema'

    DOCKER_MAIN_FILENAME = 'Dockertemplate'
    DOCKER_ENV_FILENAME = 'Dockerenv'

    RUNNER_FILENAME = 'run.sh'

    def __init__(self, env, working_path):
        self._env = env
        self.working_path = os.path.join(working_path, 'checkio_mission')
        self.path_verification = os.path.join(self.working_path, self.DIR_VERIFICATION)
        self.path_runner = os.path.join(self.path_verification, 'envs', self.RUNNER_FILENAME)

    def compile_from_files(self, source_path):
        repository = self.get_base_repository(source_path)
        self.git_pull(repository, self.working_path)
        self.copy_user_files(source_path)
        self.make_env_runner()
        self.make_dockerfile()
        return self.path_verification

    def compile_from_git(self, repository):
        source_path = None
        try:
            source_path = tempfile.mkdtemp()
            self.git_pull(repository, source_path)
            return self.compile_from_files(source_path)
        finally:
            if source_path is not None:
                shutil.rmtree(source_path)

    def get_base_repository(self, source_path):
        """
        Parse schema file of CheckiO mission
        :param source_path: path to CheckiO mission
        :return: return base repository of mission
        """
        schema_file = os.path.join(source_path, self.SCHEMA_FILENAME)
        if not os.path.exists(schema_file):
            raise MissionFilesException('Schema file does not exists.')

        with open(schema_file, 'r') as f:
            content = f.readline()
        if not content:
            raise MissionFilesException('Schema file is empty')
        parts = content.split(';', 1)
        if len(parts) != 2:
            raise MissionFilesException('Schema content is wrong')
        url = parts[1].strip()
        branch = None
        if not url.startswith('git@github.com') and '@' in url:
            repository_parts = url.split('@', 1)
            url = repository_parts[0].strip()
            branch = repository_parts[1].strip()
        return {
            'url': url,
            'branch': branch
        }

    def git_pull(self, repository, destination_path):
        try:
            repo = git.Repo.clone_from(repository['url'], destination_path)
        except git.GitCommandError as e:
            raise Exception(u"{}, {}".format(e or '', e.stderr))
        branch = repository.get('branch')
        if branch is not None:
            g = git.Git(repo.working_dir)
            g.checkout(branch)

    def copy_user_files(self, source_path):
        copy_tree(source_path, self.working_path)

    def make_env_runner(self):
        runner_template = self._get_file_content(self.path_runner)
        runner_template = runner_template.replace('{{env}}', self._env)
        with open(self.path_runner, 'w') as f:
            f.write(runner_template)

    def make_dockerfile(self):
        docker_main_file = os.path.join(self.path_verification, self.DOCKER_MAIN_FILENAME)
        docker_env_file = os.path.join(self.path_verification, 'envs', self._env,
                                       self.DOCKER_ENV_FILENAME)

        docker_main = self._get_file_content(docker_main_file)
        docker_env = self._get_file_content(docker_env_file)

        docker_main = docker_main.replace('{{env_instructions}}', docker_env)
        docker_main = docker_main.replace('{{env}}', self._env)

        dockerfile_path = os.path.join(self.path_verification, 'Dockerfile')
        with open(dockerfile_path, 'w') as f:
            f.write(docker_main)

    def _get_file_content(self, file):
        with open(file, "r") as file:
            return file.read()
