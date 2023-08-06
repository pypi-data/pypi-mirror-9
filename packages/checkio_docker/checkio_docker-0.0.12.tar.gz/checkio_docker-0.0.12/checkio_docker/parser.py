import os
import git
import shutil
import tempfile
from distutils.dir_util import copy_tree


class MissionFilesException(Exception):
    pass


class MissionFilesCompiler(object):

    DIR_VERIFICATION = 'verification'
    DIR_VERIFICATION_ENVS = 'envs'
    DIR_INITIAL_CODES = 'initial'

    SCHEMA_FILENAME = 'schema'

    DOCKER_MAIN_FILENAME = 'Dockertemplate'
    DOCKER_ENV_FILENAME = 'Dockerenv'


    def __init__(self, working_path):
        self.working_path = working_path
        self.path_verification = os.path.join(self.working_path, self.DIR_VERIFICATION)
        self.path_envs = os.path.join(self.path_verification, self.DIR_VERIFICATION_ENVS)
        self.path_initial = os.path.join(self.working_path, self.DIR_INITIAL_CODES)

    def compile_from_files(self, source_path):
        base_repositories = self.download_base_repositories(source_path)
        if base_repositories:
            base_repositories.reverse()
            for repository_path in base_repositories:
                copy_tree(repository_path, self.working_path)
                shutil.rmtree(repository_path)
        self.copy_user_files(source_path)
        active_envs = self.get_active_envs()
        self.filter_envs(active_envs)
        self.make_dockerfile(active_envs)
        return self.path_verification

    def download_base_repositories(self, source_path):
        repository = self.get_base_repository(source_path)
        base_repositories = []
        while repository is not None:
            base_repository_path = tempfile.mkdtemp()
            self.git_pull(repository, base_repository_path)
            base_repositories.append(base_repository_path)
            repository = self.get_base_repository(base_repository_path)
        return base_repositories

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
            return None

        with open(schema_file, 'r') as f:
            content = f.readline()
        if not content:
            raise MissionFilesException('Schema file is empty')
        parts = content.split(';', 1)
        if len(parts) != 2:
            raise MissionFilesException('Schema content is wrong')
        url = parts[1].strip()
        branch = None
        if '@' in url:
            repository_parts = url.split('@', 1)
            if ':' not in repository_parts[1]:
            # exclude `git@github.com:CheckiO/mission-template.git`
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

    def get_active_envs(self):
        return os.listdir(self.path_initial)

    def filter_envs(self, active_envs):
        for env in os.listdir(self.path_envs):
            if env not in active_envs:
                shutil.rmtree(os.path.join(self.path_envs, env))

    def make_dockerfile(self, active_envs):
        envs_docker = []
        for env in active_envs:
            docker_env_file = os.path.join(self.path_verification, 'envs', env, self.DOCKER_ENV_FILENAME)
            docker_env_content = self._get_file_content(docker_env_file)
            envs_docker.append(docker_env_content.replace('{{env}}', env))

        docker_main_file = os.path.join(self.path_verification, self.DOCKER_MAIN_FILENAME)
        docker_main = self._get_file_content(docker_main_file)

        docker_main = docker_main.replace('{{env_instructions}}', "\n".join(envs_docker))
        dockerfile_path = os.path.join(self.path_verification, 'Dockerfile')
        with open(dockerfile_path, 'w') as f:
            f.write(docker_main)

    def _get_file_content(self, file):
        with open(file, "r") as file:
            return file.read()
