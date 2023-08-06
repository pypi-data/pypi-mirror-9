# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#

from __future__ import unicode_literals
from __future__ import division

# FOR WINDOWS INSTALL OF psycopg2
# http://stickpeople.com/projects/python/win-psycopg/2.6.0/psycopg2-2.6.0.win32-py2.7-pg9.4.1-release.exe
import psycopg2
from pyLibrary import convert
from pyLibrary.jsons import Log
from pyLibrary.meta import use_settings
from pyLibrary.strings import expand_template


class Postgres(object):


    @use_settings
    def __init__(self, host, user, password, database=None, port=5439, settings=None):
        self.settings=settings

    def __enter__(self):
        self.connection=psycopg2.connect(
            database=self.settings.database,
            user=self.settings.user,
            password=self.settings.password,
            host=self.settings.host,
            port=self.settings.port
        )
        self.cursor= self.connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.close()

    def query(self, sql, param=None):
        if param:
            sql = expand_template(sql, self.quote_param(param))
        output = self.cursor.fetchall()
        return output

    def execute(self, command, param):
        if param:
            sql = expand_template(command, self.quote_param(param))

        self.cursor.execute(command)

    def insert(self, table_name, record):
        keys = record.keys()

        try:
            command = "INSERT INTO " + self.quote_column(table_name) + "(" + \
                      ",".join([self.quote_column(k) for k in keys]) + \
                      ") VALUES (" + \
                      ",".join([self.quote_value(record[k]) for k in keys]) + \
                      ")"

            self.execute(command)
        except Exception, e:
            Log.error("problem with record: {{record}}", {"record": record}, e)

    def quote_param(self, param):
        return {k: self.quote_value(v) for k, v in param.items()}

    def quote_column(self, name):
        return convert.string2quote(name)

    def quote_value(self, value):
        self.cursor.mogrify('%s', value)
