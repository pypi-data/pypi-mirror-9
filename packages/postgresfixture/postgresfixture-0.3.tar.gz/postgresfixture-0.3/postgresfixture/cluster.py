# Copyright 2012-2014 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Manage a PostgreSQL cluster."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "Cluster",
    "PG_VERSION_MAX",
    "PG_VERSIONS",
    ]

from contextlib import (
    closing,
    contextmanager,
    )
from distutils.version import LooseVersion
from fcntl import (
    LOCK_EX,
    LOCK_UN,
    lockf,
    )
from functools import wraps
from glob import iglob
from os import (
    devnull,
    environ,
    makedirs,
    path,
    )
import pipes
from shutil import rmtree
from subprocess import (
    CalledProcessError,
    check_call,
    )

import psycopg2


PG_BASE = "/usr/lib/postgresql"

PG_VERSION_BINS = {
    path.basename(pgdir): path.join(pgdir, "bin")
    for pgdir in iglob(path.join(PG_BASE, "*"))
    if path.exists(path.join(pgdir, "bin", "pg_ctl"))
}

PG_VERSION_MAX = max(PG_VERSION_BINS, key=LooseVersion)
PG_VERSIONS = sorted(PG_VERSION_BINS, key=LooseVersion)


def get_pg_bin(version):
    """Return the PostgreSQL ``bin`` directory for the given `version`."""
    return PG_VERSION_BINS[version]


def path_with_pg_bin(exe_path, version):
    """Return `exe_path` with the PostgreSQL ``bin`` directory added."""
    exe_path = [
        elem for elem in exe_path.split(path.pathsep)
        if len(elem) != 0 and not elem.isspace()
        ]
    pg_bin = get_pg_bin(version)
    if pg_bin not in exe_path:
        exe_path.insert(0, pg_bin)
    return path.pathsep.join(exe_path)


def locked(method):
    """Execute the decorated method with its instance's lock held."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)
    return wrapper


class Cluster:
    """Represents a PostgreSQL cluster, running or not."""

    def __init__(self, datadir, version=PG_VERSION_MAX):
        self.datadir = path.abspath(datadir)
        self.version = version
        self.lockfile = path.join(
            path.dirname(self.datadir),
            ".%s.lock" % path.basename(self.datadir))

    @property
    @contextmanager
    def lock(self):
        """Context that takes out a lock for critical sections.

        The lock is meant to be short-lived, to avoid race conditions. As
        such, acquiring this lock will block.
        """
        with open(self.lockfile, "ab") as fd:
            lockf(fd, LOCK_EX)
            try:
                yield
            finally:
                lockf(fd, LOCK_UN)

    @locked
    def execute(self, *command, **options):
        """Execute a command with an environment suitable for this cluster."""
        env = options.pop("env", environ).copy()
        env["PATH"] = path_with_pg_bin(env.get("PATH", ""), self.version)
        env["PGDATA"] = env["PGHOST"] = self.datadir
        check_call(command, env=env, **options)

    @property
    def exists(self):
        """Whether or not this cluster exists on disk."""
        version_file = path.join(self.datadir, "PG_VERSION")
        return path.exists(version_file)

    @property
    def pidfile(self):
        """The (expected) pidfile for a running cluster.

        Does *not* guarantee that the pidfile exists.
        """
        return path.join(self.datadir, "postmaster.pid")

    @property
    def logfile(self):
        """The log file used (or will be used) by this cluster."""
        return path.join(self.datadir, "backend.log")

    @property
    def running(self):
        """Whether this cluster is running or not."""
        with open(devnull, "wb") as null:
            try:
                self.execute("pg_ctl", "status", stdout=null)
            except CalledProcessError as error:
                # pg_ctl in PostgreSQL 9.1 returns 1 when the server is
                # not running, whereas it returns 3 in PostgreSQL 9.2
                # and later. This checks for specific codes to avoid
                # masking errors from insufficient permissions or
                # missing executables, for example.
                if LooseVersion(self.version) >= LooseVersion("9.2"):
                    if error.returncode == 3:
                        return False
                else:
                    if error.returncode == 1:
                        return False
                # Some other error: moan about it.
                raise
            else:
                return True

    @locked
    def create(self):
        """Create this cluster, if it does not exist."""
        if not self.exists:
            if not path.isdir(self.datadir):
                makedirs(self.datadir)
            self.execute("pg_ctl", "init", "-s", "-o", "-E utf8 -A trust")

    @locked
    def start(self):
        """Start this cluster, if it's not already started."""
        if not self.running:
            self.create()
            # pg_ctl options:
            #  -l <file> -- log file.
            #  -s -- no informational messages.
            #  -w -- wait until startup is complete.
            # postgres options:
            #  -h <arg> -- host name; empty arg means Unix socket only.
            #  -F -- don't bother fsync'ing.
            #  -k -- socket directory.
            self.execute(
                "pg_ctl", "start", "-l", self.logfile, "-s", "-w",
                "-o", "-h '' -F -k %s" % pipes.quote(self.datadir))

    def connect(self, database="template1", autocommit=True):
        """Connect to this cluster.

        Starts the cluster if necessary.
        """
        self.start()
        connection = psycopg2.connect(
            database=database, host=self.datadir)
        connection.autocommit = autocommit
        return connection

    def shell(self, database="template1"):
        self.execute("psql", "--quiet", "--", database)

    @property
    def databases(self):
        """The names of databases in this cluster."""
        with closing(self.connect("postgres")) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("SELECT datname FROM pg_catalog.pg_database")
                return {name for (name,) in cur.fetchall()}

    def createdb(self, name):
        """Create the named database."""
        with closing(self.connect()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("CREATE DATABASE %s" % name)

    def dropdb(self, name):
        """Drop the named database."""
        with closing(self.connect()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("DROP DATABASE %s" % name)

    @locked
    def stop(self):
        """Stop this cluster, if started."""
        if self.running:
            # pg_ctl options:
            #  -w -- wait for shutdown to complete.
            #  -m <mode> -- shutdown mode.
            self.execute("pg_ctl", "stop", "-s", "-w", "-m", "fast")

    @locked
    def destroy(self):
        """Destroy this cluster, if it exists.

        The cluster will be stopped if it's started.
        """
        if self.exists:
            self.stop()
            rmtree(self.datadir)
