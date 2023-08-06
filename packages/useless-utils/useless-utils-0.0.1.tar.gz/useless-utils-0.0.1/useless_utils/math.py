#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @file     generators
# @author   kaka_ace <xiang.ace@gmail.com>
# @date     Mar 04 2015
# @breif     
# 


import sys
if sys.version_info < (3, 0):
    range = xrange
else:
    from functools import reduce

import math

from contextlib import contextmanager

def _fibonacci_formula(i):
    return int(((1 + math.sqrt(5)) / 2) ** i / math.sqrt(5) + 0.5)


class FibonacciUtils(object):
    """
        s = \"\"\"
        def fibonacci():
            a, b = 0, 1
            while True:
                yield a + b
                a, b = b, a + b

        g = fibonacci()

        i = 1
        while i <= 10:
            i += 1
            next(g)
            # print(v)
        \"\"\"

        s2 = \"\"\"
        import math

        i = 2
        while i <= 11:
            d = int(((1 + math.sqrt(5)) / 2) ** i / math.sqrt(5) + 0.5)
            i += 1
            # print(d)

        \"\"\"

        import timeit

        t1 = timeit.timeit(stmt=s, number=10)

        t2 = timeit.timeit(stmt=s2, number=10)

        print("t1: ", t1)
        print("t2: ", t2)

        # t1:  0.0004139620004934841
        # t2:  0.00016210499961744063

        mathematics is always faster than yield
    """
    _FIBONACCI_FIRST_70_LIST = [_fibonacci_formula(i) for i in range(0, 71)]

    @staticmethod
    def fibonacci_calculator(n):
        """
        :param n: integer, cacalute the nth value

        inspired from:
        http://stackoverflow.com/questions/4935957/fibonacci-numbers-with-an-one-liner-in-python-3

        :return: the last result value
        """
        # if n in (0, 1):
        #     return n

        if n < 71:
            return FibonacciUtils._FIBONACCI_FIRST_70_LIST[n]

        starts = (
            FibonacciUtils._FIBONACCI_FIRST_70_LIST[69],
            FibonacciUtils._FIBONACCI_FIRST_70_LIST[70],
        )

        i, g = 71, FibonacciUtils.fibonacci(starts)
        while i < n:
            i += 1
            next(g)
        v = next(g)
        return v

    @staticmethod
    def fibonacci(starts=None):
        """
        :param: starts is a tuple
            default (0, 1)
        :return: generator function
        """
        if starts is None:
            a, b = 0, 1
        else:
            a, b = starts[0], starts[1]

        while True:
            yield a + b
            a, b = b, a + b

    @staticmethod
    def get_fibonacci_generator():
        """
        init with 0, 1
        :return: generator
        """
        return FibonacciUtils.fibonacci()