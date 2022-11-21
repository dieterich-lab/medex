from os.path import dirname, join
from shutil import which
from subprocess import run
from typing import List


def pytest_sessionstart(session):  # noqa
    cmd = _get_docker_call()
    cmd.extend(['up', '-d'])
    cwd = _get_docker_folder()
    run(cmd, cwd=cwd, check=True)


def pytest_sessionfinish(session, exitstatus):  # noqa
    cmd = _get_docker_call()
    cmd.append('down')
    cwd = _get_docker_folder()
    run(cmd, cwd=cwd, check=True)


def _get_docker_call() -> List[str]:
    docker_compose = which('docker-compose')
    if docker_compose is None:
        docker = which('docker')
        if docker is None:
            raise Exception('No docker found!')
        return [docker, 'compose']
    else:
        return [docker_compose]


def _get_docker_folder():
    return join(dirname(__file__), 'docker')
