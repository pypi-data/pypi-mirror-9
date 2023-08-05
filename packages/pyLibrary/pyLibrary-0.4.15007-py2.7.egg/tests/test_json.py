# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#

# from __future__ import unicode_literals
import datetime
import unittest
from pyLibrary import convert
from pyLibrary.debugs.logs import Log
from pyLibrary.dot import Dict


class TestJSON(unittest.TestCase):
    def test_date(self):
        output = convert.value2json({"test": datetime.date(2013, 11, 13)})
        Log.note("JSON = {{json}}", {"json": output})


    def test_unicode1(self):
        output = convert.value2json({"comment": u"Open all links in the current tab, except the pages opened from external apps â€” open these ones in new windows"})
        assert output == u'{"comment": "Open all links in the current tab, except the pages opened from external apps â€” open these ones in new windows"}'

        if not isinstance(output, unicode):
            Log.error("expecting unicode json")

    def test_unicode2(self):
        output = convert.value2json({"comment": b"testing accented char àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"})

        assert output == u'{"comment": "testing accented char àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"}'
        if not isinstance(output, unicode):
            Log.error("expecting unicode json")

    def test_unicode3(self):
        output = convert.value2json({"comment": u"testing accented char ŕáâăäĺćçčéęëěíîďđńňóôőö÷řůúűüýţ˙"})
        assert output == u'{"comment": "testing accented char ŕáâăäĺćçčéęëěíîďđńňóôőö÷řůúűüýţ˙"}'
        if not isinstance(output, unicode):
            Log.error("expecting unicode json")

    def test_double(self):
        test = {"value": 5.2025595183536973e-07}
        output = convert.value2json(test)
        if output != u'{"value": 5.202559518353697e-07}':
            Log.error("expecting correct value")

    def test_generator(self):
        test = {"value": (x for x in [])}
        output = convert.value2json(test)
        if output != u'{"value": []}':
            Log.error("expecting correct value")

    def test_bad_key(self):
        test = {24: "value"}
        output = convert.value2json(test)


    def test_default_python(self):

        test = {"add": Dict(start=b"".join([" ", u"â€"]))}
        output = convert.value2json(test)

        expecting = u'{"add": {"start": " â€"}}'
        self.assertEqual(expecting, output, "expecting correct json")






if __name__ == '__main__':
    try:
        Log.start()
        unittest.main()
    finally:
        Log.stop()
