
.. role:: red

.. raw:: html

    <style> .red {color: red; font-weight: bold} </style>



=====================================
RunTask, Coherent Time Task Scheduler
=====================================

Introduction
============

**RunTask** is a python module implementing a coherent time task scheduler
in a very simple way. The execution order of all controlled tasks is stricktly
predictable and execution times are aligned to given reference times.

Suppose to have tasks A, B, C that need to be run at the beginning of each
minute, in that order. In addition, suppose to have tasks D, E, F that need
to be run at the begining of each second, in that order. Moreover, since the
beginning of each minute is coincident with the beginning of a second, it is
wanted that the task group A, B, C is run before the task group D, E, F.
RunTask is designed to fulfill all these kind of requirements.

This is the documentation for version |version|.

RunTask is released under the GNU General Public License.

At present, version |version|, RunTask is in alpha status. Any debugging aid is
welcome.

For any question, suggestion, contribution contact the author Fabrizio Pollastri <f.pollastri_a_t_inrim.it>.

Features
========

* All controlled tasks are run within the same thread, so with respect to each
  other, they are thread safe.
* Tasks are callables with theirs arguments.
* When a task execution time is delayed by cpu load more then the task period,
  that execution is skipped.
* Each task execution can be single shot, periodic forever or periodic
  for a given number of runs.
* Each task execution time is computed from a given reference time, so 
  the phase between different execution periods can be easily controlled.
* Tasks having the same execution time are grouped by run period and
  run from longest to shortest period. Within each group, tasks are
  run following the task registration order.

Caveats
=======

*RunTask* is not a preemptive scheduler, so all tasks are run sequentially
when their run time is reached.
 
Since all tasks are run within the same thread, all tasks must be
non-blocking.

The tasks controlled by RunTask are thread safe with respect to each other.
Since, RunTask is instantiated by a main program, the controlled tasks
are NOT thread safe with respect to the main program.

Requirements
============

To run the code, **Python 2.6 or later** must
already be installed.  The latest release is recommended.  Python is
available from http://www.python.org/.


Installation
============

1. Open a shell.

2. Get root privileges and install the package. Command::

    pip install runtask
