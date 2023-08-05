"""Service fixtures."""
from distutils.spawn import find_executable
import re
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess
import time
import uuid

import pytest

WRONG_FILE_NAME_CHARS_RE = re.compile('[^\w_-]')


@pytest.fixture(scope='session')
def run_services(request, slave_id):
    """Indicate whether the services should run or not."""
    return slave_id != 'local' or request.config.option.run_services


@pytest.fixture(scope='session')
def slave_id(request):
    """
    The id of the slave if tests are run using xdist.

    It is set to `'local'` if tests are not run using xdist.

    The id is unique for a test run. An id may clash if there are two workers
    that belong to different test sessions.

    """
    return WRONG_FILE_NAME_CHARS_RE.sub('_', getattr(request.config, 'slaveinput', {}).get('slaveid', 'local'))


@pytest.fixture(scope='session')
def session_id(request, slave_id, run_services):
    """The test session id.

    It is supposed to be globally unique.

    """
    # UUID should be enough, other fields are added for the debugging purposes.
    session_id = '{random}-{slave_id}'.format(
        random=uuid.uuid4().hex,
        slave_id=slave_id,
    )

    return session_id


@pytest.fixture(scope='session')
def watcher_getter(request, services_log):
    """Popen object of given executable name and it's arguments.

    Wait for the process to start.
    Add finalizer to properly stop it.
    """
    def watcher_getter_function(name, arguments=None, timeout=20, checker=None):
        executable = find_executable(name)
        assert executable, 'You have to install {0} executable.'.format(name)

        cmd = [name] + arguments or []

        services_log.debug('Starting {0}: {1}'.format(name, arguments))

        watcher = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
        )

        def finalize():
            watcher.kill()
            try:
                watcher.communicate(timeout=timeout / 2)
            except subprocess.TimeoutExpired:
                watcher.terminate()
                watcher.communicate(timeout=timeout / 2)
        request.addfinalizer(finalize)

        # Wait for memcached to accept connections.
        times = 0
        while not checker():

            if watcher.poll() is not None:
                output, err = watcher.communicate()
                raise Exception("Error running memcached: {0}".format(err))

            if times > timeout:
                raise Exception('The memcached socket could not be found!')

            time.sleep(1)
            times += 1

        return watcher

    return watcher_getter_function
