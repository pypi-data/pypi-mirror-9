from __future__ import unicode_literals

import contextlib
import distutils.spawn
import os

import virtualenv

from pre_commit.languages import helpers
from pre_commit.util import clean_path_on_failure


ENVIRONMENT_DIR = 'py_env'


class PythonEnv(helpers.Environment):
    @property
    def env_prefix(self):
        return ". '{{prefix}}{0}activate' &&".format(
            virtualenv.path_locations(
                ENVIRONMENT_DIR,
            )[-1].rstrip(os.sep) + os.sep,
            'activate',
        )


@contextlib.contextmanager
def in_env(repo_cmd_runner):
    yield PythonEnv(repo_cmd_runner)


def norm_version(version):
    if os.name == 'nt':  # pragma: no cover (windows)
        if not distutils.spawn.find_executable(version):
            # The default place for python on windows is:
            # C:\PythonXX\python.exe
            version = r'C:\{0}\python.exe'.format(version.replace('.', ''))
    return version


def install_environment(repo_cmd_runner, version='default'):
    assert repo_cmd_runner.exists('setup.py')

    # Install a virtualenv
    with clean_path_on_failure(repo_cmd_runner.path(ENVIRONMENT_DIR)):
        venv_cmd = ['virtualenv', '{{prefix}}{0}'.format(ENVIRONMENT_DIR)]
        if version != 'default':
            venv_cmd.extend(['-p', norm_version(version)])
        repo_cmd_runner.run(venv_cmd)
        with in_env(repo_cmd_runner) as env:
            env.run("cd '{prefix}' && pip install .")


def run_hook(repo_cmd_runner, hook, file_args):
    with in_env(repo_cmd_runner) as env:
        return helpers.run_hook(env, hook, file_args)
