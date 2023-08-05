#!/usr/bin/env python2.7

from __future__ import print_function
import os
import pprint
import sys
import time
import platform
#import psutil
import locale


verbose_print  = print if True else lambda *a, **k: None


def print_log_header():
    """Print a standardized header for the log with starting conditions."""
    verbose_print("# Working Directory : %s" % os.getcwd())
    pbs_jobid = os.environ.get("PBS_JOBID")
    if pbs_jobid:
        verbose_print("# $PBS_JOBID        : %s" % pbs_jobid)
    verbose_print("# Hostname          : %s" % platform.node())
    locale.setlocale(locale.LC_ALL, '')
    ram_bytes = 64000000000 / 1024 / 1024
    ram_str = locale.format("%d", ram_bytes, grouping=True)
    verbose_print("# RAM               : %s MB" % ram_str)
    verbose_print("# Python Version    : %s" % sys.version.replace("\n", " "))
    verbose_print("")

print_log_header()