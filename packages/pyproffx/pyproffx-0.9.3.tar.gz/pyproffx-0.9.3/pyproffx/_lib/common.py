# Copyright (C) 2015 Haruhiko Matsuo <halm.matsuo@gmail.com>
#
#  Distributed under the MIT License.
#  See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT

"""Decorators"""

from functools import wraps
from itertools import product
import numpy as np


def tag_maker(counter_method):
    """This is a decorator function creating a key for
    the PA event dictionary.

    Parameters
    ----------
        monitor_level :  monitor level
            'Application' (or 'A'), 'Process' ('P'), 'Thread' ('T')
        pid: process id (MPI rank)
        tid: thread id
    """
    def _tag_expander(*tag_in):
        """If the monitor level is given by its acronym,
        it is expand to the long form before it is passed to
        the decorator."""
        if tag_in[1][0] == 'T':
            monitor_level = 'Thread'
            pid = tag_in[2]
            tid = tag_in[3]
            tag = (tag_in[0], monitor_level, pid, tid)
        elif tag_in[1][0] == 'P':
            monitor_level = 'Process'
            pid = tag_in[2]
            tag = (tag_in[0], monitor_level, pid)
        elif tag_in[1][0] == 'A':
            monitor_level = 'Application'
            tag = (tag_in[0], monitor_level)
        else:
            print("error")
        return tag

    @wraps(counter_method)
    def _tag_maker(*args):
        """decorator"""
        tag = _tag_expander(*args)
        res = counter_method(*tag)
        return res
    return _tag_maker


def element_wise(counter_method):
    """This is a decorator function allowing multi-process/thread input.

    Note that this decorator should always follow the decorator 'tag_maker'.
    """
    def _make_iterator(*args):
        """Make a compound iterator from a process iterator and
        a thread one.

        Note that 'Application' case should not execute this
        function."""

        monitor_level = args[1]

        arg_pid = args[2]
        if hasattr(arg_pid, '__iter__'):
            pid_itr = (i for i in xrange(arg_pid[0], arg_pid[1]))
        else:
            pid_itr = (arg_pid,)

        if monitor_level == 'Thread':
            arg_tid = args[3]
            if hasattr(arg_tid, '__iter__'):
                tid_itr = (i for i in xrange(arg_tid[0], arg_tid[1]))
            else:
                tid_itr = (arg_tid,)

        if monitor_level == 'Process':
            return_itr = pid_itr
        elif monitor_level == 'Thread':
            return_itr = (pid_itr, tid_itr)

        return return_itr

    @wraps(counter_method)
    def _element_wise(*args):
        """Distribute multi-process/thread input"""
        if args[1] == 'Thread':
            pid_itr, tid_itr = _make_iterator(*args)
            retval = [counter_method(args[0], args[1], pid, tid)
                      for pid, tid in product(pid_itr, tid_itr)]
            return np.array(retval)
        elif args[1] == 'Process':
            pid_itr = _make_iterator(*args)
            retval = [counter_method(args[0], args[1], pid) for pid in pid_itr]
            return np.array(retval)
        elif args[1] == 'Application':
            return np.array(counter_method(*args))
        else:
            print 'Unknown monitor level'
    return _element_wise


def return_val_unit(counter_method):
    """Convert cycle counts to another unit.

    The unit can be 'sec' (default), 'rate', or 'cycle'.
    """
    @wraps(counter_method)
    def _return_val_unit(*args, **kwargs):
        if kwargs == {}:
            ret_unit = 'sec'
        else:
            ret_unit = kwargs['unit']

        if ret_unit == 'sec':
            cycle_counts = args[0].d.cycle_counts1(*args[1:])  # exclude 'self'
            cpu_cycle = args[0].e[0][2] * 1.0e6  # Convert MHz to Hz
            res = counter_method(*args) / cpu_cycle
        elif ret_unit == 'rate':
            cycle_counts = args[0].d.cycle_counts1(*args[1:])  # exclude 'self'
            if hasattr(cycle_counts, '__getitem__'):
                res = counter_method(*args) / cycle_counts.astype(float)
            else:
                res = counter_method(*args) / float(cycle_counts)
        elif ret_unit == 'cycle':
            res = counter_method(*args)

        return res
    return _return_val_unit


def monitor_level_checker(counter_method):
    """This is a decorator function checking monitor level.
    """
    def _check_monitor_level(*tag_in):
        d = tag_in[0].d  # self.RawDat
        ml = tag_in[1][0]  # monitor level

        bad_mon_lev = '[Invalid monitor level] '
        if d.is_hybrid and ml != 'T':
            raise Exception(bad_mon_lev + 'Use monitor level: Thread.')
        elif d.is_thread and ml != 'T':
            raise Exception(bad_mon_lev + 'Use monitor level: Thread.')
        elif d.is_flatmpi and ml != 'P':
            raise Exception(bad_mon_lev + 'Use monitor level: Process.')
        elif d.is_single and ml != 'A':
            raise Exception(bad_mon_lev + 'Use monitor level: Application.')

    @wraps(counter_method)
    def _monitor_level_checker(*args):
        """decorator"""
        _check_monitor_level(*args)
        res = counter_method(*args)
        return res
    return _monitor_level_checker
