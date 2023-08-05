# -*- coding: utf8 -*-

import logging
import os
import platform
import tempfile
import time
import uuid
from datetime import datetime

import pytz

log = logging.getLogger(__name__)


class PidFile(object):
    """ A small helper class for pidfiles. """

    PID_DIR = '/var/run/whale-agent'

    def __init__(self, program, pid_dir=None):
        self.pid_file = "%s.pid" % program
        self.pid_dir = pid_dir or self.get_default_pid_dir()
        self.pid_path = os.path.join(self.pid_dir, self.pid_file)

    def get_default_pid_dir(self):
        return PidFile.PID_DIR

    def get_path(self):
        # Can we write to the directory
        try:
            if os.access(self.pid_dir, os.W_OK):
                log.info("Pid file is: %s" % self.pid_path)
                return self.pid_path
        except OSError:
            log.warn("Cannot locate pid file, trying to use: %s" % tempfile.gettempdir())

        # if all else fails
        if os.access(tempfile.gettempdir(), os.W_OK):
            tmp_path = os.path.join(tempfile.gettempdir(), self.pid_file)
            log.debug("Using temporary pid file: %s" % tmp_path)
            return tmp_path

        else:
            # Can't save pid file, bail out
            log.error("Cannot save pid file anywhere")
            raise Exception("Cannot save pid file anywhere")

    def clean(self):
        try:
            path = self.get_path()
            log.debug("Cleaning up pid file %s" % path)
            os.remove(path)
            return True
        except OSError:
            log.warn("Could not clean up pid file")
            return False

    def get_pid(self):
        """
        Retrieve the actual pid
        """
        try:
            pf = open(self.get_path())
            pid_s = pf.read()
            pf.close()

            return int(pid_s.strip())
        except OSError:
            return None


def string_import(path):
    try:
        import importlib
        split = path.split('.')
        module_ = importlib.import_module(".".join(split[:-1]))
        class_ = getattr(module_, split[len(split)-1])
        return class_
    except AttributeError:
        raise ImportError('Could not import %s' % path)


def create_timestamp(date_time):
    return time.mktime(date_time.timetuple())*1000


def create_datetime(unix_timestamp):
    try:
        date = datetime.utcfromtimestamp(unix_timestamp)
    except ValueError:
        date = datetime.utcfromtimestamp(unix_timestamp/1000)

    date = make_aware(date, pytz.UTC)

    return date


def make_aware(value, timezone):
    if hasattr(timezone, 'localize'):
        return timezone.localize(value, is_dst=None)
    else:
        if is_aware(value):
            raise ValueError(
                "make_aware expects a naive datetime, got %s" % value)
        return value.replace(tzinfo=timezone)


def is_aware(value):
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None


def get_uuid():
    return uuid.uuid5(uuid.NAMESPACE_DNS, platform.node() + str(uuid.getnode())).hex
