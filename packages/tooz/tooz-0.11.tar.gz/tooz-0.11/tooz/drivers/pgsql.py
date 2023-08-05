# -*- coding: utf-8 -*-
#
# Copyright © 2014 eNovance
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import contextlib
import hashlib

import psycopg2
import six

import tooz
from tooz import coordination
from tooz.drivers import _retry
from tooz import locking
from tooz import utils


# See: psycopg/diagnostics_type.c for what kind of fields these
# objects may have (things like 'schema_name', 'internal_query'
# and so-on which are useful for figuring out what went wrong...)
_DIAGNOSTICS_ATTRS = tuple([
    'column_name',
    'constraint_name',
    'context',
    'datatype_name',
    'internal_position',
    'internal_query',
    'message_detail',
    'message_hint',
    'message_primary',
    'schema_name',
    'severity',
    'source_file',
    'source_function',
    'source_line',
    'sqlstate',
    'statement_position',
    'table_name',
])


def _format_exception(e):
    lines = [
        "%s: %s" % (type(e).__name__, utils.exception_message(e).strip()),
    ]
    if hasattr(e, 'pgcode') and e.pgcode is not None:
        lines.append("Error code: %s" % e.pgcode)
    # The reason this hasattr check is done is that the 'diag' may not always
    # be present, depending on how new of a psycopg is installed... so better
    # to be safe than sorry...
    if hasattr(e, 'diag') and e.diag is not None:
        diagnostic_lines = []
        for attr_name in _DIAGNOSTICS_ATTRS:
            if not hasattr(e.diag, attr_name):
                continue
            attr_value = getattr(e.diag, attr_name)
            if attr_value is None:
                continue
            diagnostic_lines.append("  %s = %s" (attr_name, attr_value))
        if diagnostic_lines:
            lines.append('Diagnostics:')
            lines.extend(diagnostic_lines)
    return "\n".join(lines)


@contextlib.contextmanager
def _translating_cursor(conn):
    try:
        with conn.cursor() as cur:
            yield cur
    except psycopg2.Error as e:
        raise coordination.ToozError(_format_exception(e))


class PostgresLock(locking.Lock):
    """A PostgreSQL based lock."""

    def __init__(self, name, connection):
        super(PostgresLock, self).__init__(name)
        self._conn = connection
        h = hashlib.md5()
        h.update(name)
        if six.PY2:
            self.key = list(map(ord, h.digest()[0:2]))
        else:
            self.key = h.digest()[0:2]

    def acquire(self, blocking=True):
        if blocking is True:
            with _translating_cursor(self._conn) as cur:
                cur.execute("SELECT pg_advisory_lock(%s, %s);", self.key)
                return True
        elif blocking is False:
            with _translating_cursor(self._conn) as cur:
                cur.execute("SELECT pg_try_advisory_lock(%s, %s);", self.key)
                return cur.fetchone()[0]
        else:
            def _acquire():
                with _translating_cursor(self._conn) as cur:
                    cur.execute("SELECT pg_try_advisory_lock(%s, %s);",
                                self.key)
                    if cur.fetchone()[0] is True:
                        return True
                    raise _retry.Retry
            kwargs = _retry.RETRYING_KWARGS.copy()
            kwargs['stop_max_delay'] = blocking
            return _retry.Retrying(**kwargs).call(_acquire)

    def release(self):
        with _translating_cursor(self._conn) as cur:
            cur.execute("SELECT pg_advisory_unlock(%s, %s);", self.key)
            return cur.fetchone()[0]


class PostgresDriver(coordination.CoordinationDriver):
    """A PostgreSQL based driver."""

    def __init__(self, member_id, parsed_url, options):
        """Initialize the PostgreSQL driver."""
        super(PostgresDriver, self).__init__()
        self._host = options.get("host", [None])[-1]
        self._port = parsed_url.port or options.get("port", [None])[-1]
        self._dbname = parsed_url.path[1:] or options.get("dbname", [None])[-1]
        self._username = parsed_url.username
        self._password = parsed_url.password

    def _start(self):
        try:
            self._conn = psycopg2.connect(host=self._host,
                                          port=self._port,
                                          user=self._username,
                                          password=self._password,
                                          database=self._dbname)
        except psycopg2.Error as e:
            raise coordination.ToozConnectionError(_format_exception(e))

    def _stop(self):
        self._conn.close()

    def get_lock(self, name):
        return PostgresLock(name, self._conn)

    @staticmethod
    def watch_join_group(group_id, callback):
        raise tooz.NotImplemented

    @staticmethod
    def unwatch_join_group(group_id, callback):
        raise tooz.NotImplemented

    @staticmethod
    def watch_leave_group(group_id, callback):
        raise tooz.NotImplemented

    @staticmethod
    def unwatch_leave_group(group_id, callback):
        raise tooz.NotImplemented

    @staticmethod
    def watch_elected_as_leader(group_id, callback):
        raise tooz.NotImplemented

    @staticmethod
    def unwatch_elected_as_leader(group_id, callback):
        raise tooz.NotImplemented
