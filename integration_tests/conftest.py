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
    for candidate in ['podman-compose', 'docker-compose']:
        path = which(candidate)
        if path is not None:
            return [path]
    docker = which('docker')
    if docker is None:
        raise Exception('No docker found!')
    return [docker, 'compose']


def _get_docker_folder():
    return join(dirname(__file__), 'docker')
