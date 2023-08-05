#!/usr/bin/env python

"""
Use the Python DTrace consumer and run a Hello World DTrace script.

Created on Oct 10, 2011

@author: tmetsch
"""

from dtrace_ctypes.consumer import DTraceConsumer

SCRIPT = 'dtrace:::BEGIN {trace("Hello World");}'


def main():
    """
    Run DTrace...
    """
    consumer = DTraceConsumer()
    consumer.run(SCRIPT)

if __name__ == '__main__':
    main()
