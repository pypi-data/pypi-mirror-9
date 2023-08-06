"""Logging fixtures and functions."""
import contextlib
import logging

import pytest


@pytest.fixture(scope='session')
def services_log(slave_id):
    """A services_logger with the slave id."""
    return logging.getLogger('[{slave_id}] {name}'.format(name=__name__, slave_id=slave_id))


@contextlib.contextmanager
def dont_capture(request):
    """Suspend capturing of stdout by pytest."""
    capman = request.config.pluginmanager.getplugin("capturemanager")
    capman.suspendcapture()
    try:
        yield
    finally:
        capman.resumecapture()


def remove_handlers():
    """Remove root services_logging handlers."""
    handlers = []
    for handler in logging.root.handlers:
        if not isinstance(handler, logging.StreamHandler):
            handlers.append(handler)
    logging.root.handlers = handlers
