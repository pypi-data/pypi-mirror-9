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
import math
import __builtin__


from pyLibrary.strings import find_first
from pyLibrary.dot import Null, nvl


class Math(object):
    """
    MATH FUNCTIONS THAT ASSUME None IMPLY *NOT APPLICABLE* RATHER THAN *MISSING*
    LET "." BE SOME OPERATOR (+, -, *, etc)
    a.None == None
    None.a == None
    .None == None
    func(None, *kwargs)) == None
    """


    @staticmethod
    def bayesian_add(*args):
        a = args[0]
        if a >= 1 or a <= 0:
            from pyLibrary.debugs.logs import Log
            Log.error("Only allowed values *between* zero and one")

        for b in args[1:]:
            if b == None:
                continue
            if b >= 1 or b <= 0:
                Log.error("Only allowed values *between* zero and one")
            a = a * b / (a * b + (1 - a) * (1 - b))

        return a

    @staticmethod
    def bayesian_subtract(a, b):
        return Math.bayesian_add(a, 1 - b)


    @staticmethod
    def abs(v):
        if v == None:
            return Null
        return abs(v)

    @staticmethod
    def pow(v, expo):
        if v == None:
            return Null
        return math.pow(v, expo)

    @staticmethod
    def exp(v):
        if v == None:
            return Null
        return math.exp(v)

    @staticmethod
    def log(v, base=None):
        try:
            if v == None:
                return Null
            if v == 0.0:
                return -float("inf")
            if base == None:
                return math.log(v)
            return math.log(v, base)
        except Exception, e:
            from pyLibrary.debugs.logs import Log
            Log.error("error in log")


    @staticmethod
    def log10(v):
        try:
            return math.log(v, 10)
        except Exception, e:
            return Null

    # FOR GOODNESS SAKE - IF YOU PROVIDE A METHOD abs(), PLEASE PROVIDE ITS COMPLEMENT
    # x = abs(x)*sign(x)
    # FOUND IN numpy, BUT WE USUALLY DO NOT NEED TO BRING IN A BIG LIB FOR A SIMPLE DECISION
    @staticmethod
    def sign(v):
        if v == None:
            return Null
        if v < 0:
            return -1
        if v > 0:
            return +1
        return 0


    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except Exception:
            return False

    @staticmethod
    def is_finite(s):
        try:
            f = float(s)
            if abs(f) == float("+inf"):
                return False
            return True
        except Exception:
            return False


    @staticmethod
    def is_nan(s):
        return math.isnan(s)

    @staticmethod
    def is_integer(s):
        try:
            if float(s) == round(float(s), 0):
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def round(value, decimal=7, digits=None):
        """
        ROUND TO GIVEN NUMBER OF DIGITS, OR GIVEN NUMBER OF DECIMAL PLACES
        decimal - NUMBER OF SIGNIFICANT DIGITS (LESS THAN 1 IS INVALID)
        digits - NUMBER OF DIGITS AFTER DECIMAL POINT (NEGATIVE IS VALID)
        """
        if value == None:
            return None
        else:
            value = float(value)

        if digits != None:
            if value ==0:
                return __builtin__.round(value, digits)
            try:
                m = pow(10, math.ceil(math.log10(abs(value))))
                return __builtin__.round(value / m, digits) * m
            except Exception, e:
                from pyLibrary.debugs.logs import Log
                Log.error("not expected", e)

        return __builtin__.round(value, decimal)


    @staticmethod
    def floor(value, mod=None):
        """
        x == floor(x, a) + mod(x, a)  FOR ALL a
        """
        if value == None:
            return None
        mod = nvl(mod, 1)
        v = int(math.floor(value))
        return v - (v % mod)


    # RETURN A VALUE CLOSE TO value, BUT WITH SHORTER len(unicode(value))<len(unicode(value)):
    @staticmethod
    def approx_str(value):
        v = unicode(value)
        d = v.find(".")
        if d == -1:
            return value

        if Math.round(value) == value:
            return int(value)

        i = find_first(v, ["9999", "0000"], d)
        if i != -1:
            Math.round(value, decimal=i - d - 1)

        return value

    @staticmethod
    def ceiling(value, mod=1):
        return int(math.ceil(value/mod))*mod

    @staticmethod
    def count(values):
        count = 0
        for v in values:
            if v != None:
                count += 1
        return count

    @staticmethod
    def pow(n, p):
        if n == None or p == None:
            return None
        return math.pow(n, p)


    @staticmethod
    def sum(values):
        sum = 0
        for v in values:
            if v != None:
                sum += v
        return sum

    @staticmethod
    def max(*values):
        output = None
        for v in values:
            if v == None:
                continue
            elif output == None or v > output:
                output = v
            else:
                pass
        return output

    @staticmethod
    def min(*values):
        output = None
        for v in values:
            if v == None:
                continue
            elif output == None or v < output:
                output = v
            else:
                pass
        return output


def almost_equal(first, second, digits=None, places=None, delta=None):
    if first == second:
        return True

    if delta is not None:
        if abs(first - second) <= delta:
            return True
    else:
        places = nvl(places, digits, 18)
        diff = math.log10(abs(first-second))
        if diff < Math.ceiling(math.log10(first))-places:
            return True

    return False


