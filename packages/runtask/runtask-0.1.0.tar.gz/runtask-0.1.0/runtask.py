#!/usr/bin/python
# .+
# .context    : RunTask, coherent time task scheduler
# .title      : RunTask, coherent time task scheduler
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	7-Feb-2015
# .copyright  :	(c) 2015 Fabrizio Pollastri
# .license    : GNU General Public License (see below)
#
# This file is part of "RunTask, Coherent Time Task Scheduler".
#
# RunTask is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# RunTask is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.
#
# .-


#### import required modules

import math as mt      # mathematical support
import operator as op  # itemgetter
import threading as tg # multiple thread of run
import time as tm      # time support


#### define global variables

__version__ = '0.1.0'
__author__ = 'Fabrizio Pollastri <f.pollastri@inrim.it>'


#### classes

class RunTask:
    """ Implements a coherent time task scheduler.
      *time*: float/None. If float, take it as current time. If None, take
      current system time.
      *tick*: float, time resolution used in run time computations.
    """

    def __init__(self,time=None,tick=1.):

        # save arguments
        self.tick = tick

        # time default
        if time is None:
            time = tm.time()

        # times (unix time floats)
        self.time = None
        self.runtime = None
        self.second = None
        self.minute = None

        # task list and run list
        self.tasks = {}
        self.torun = []

        # update current time
        self._set(time)

        # root task
        def root_task(self):

            # run until terminate
            while True:
                # run all tasks
                self._run(tm.time())
                # if run list is empty, terminate
                if not self.torun:
                    return
                # wait until next run time comes
                if self.root_task_run.wait(self.torun[0][1] - tm.time()):
                    return

        # prepare thread for root task
        self.root_task = tg.Thread(target=root_task,args=(self,))
        self.root_task_run = tg.Event()


    def start(self,join=False):
        """ Start execution of registered tasks. If *join* is False, *start*
        returns immediately to the calling program. If *join* is True, *start*
        returns only when *stop* is called by a registered task. """

        # update current time
        self._set(tm.time())

        # put all tasks on the run list, computing the first run time.
        for task_id,(task,args,kargs,period,epoch,count) \
            in self.tasks.iteritems():
            first_run = self.runtime+period-mt.fmod(self.runtime-epoch,period)
            self.torun.append((task_id,first_run))

        # sort run list by ascending runtime
        self.torun = sorted(self.torun,key=op.itemgetter(1))

        # start thread
        self.root_task.start()

        # if required join thread
        if join:
            self.root_task.join()


    def stop(self):
        """ Stop execution of registered tasks. """

        self.root_task_run._set()
        self.root_task.join()


    def task(self,task,args,kargs,period,epoch=0.0,runs=-1):
        """ Register a task to be run.

          **task**: callable, a function, the task to be run.

          **args**: list/tuple, function positional arguments.

          **kargs**: dictionary, function keyword arguments.

          **period**: float, time elapse between task runs.

          **epoch**: float, reference time to assign to the first task run.

          **runs**: integer, number of task runs. If -1, run task forever.

        All times are in unix format, a float whose units are seconds from the
        beginning of epoch. 
        """

        # save task to tasks list
        task_id = len(self.tasks)
        self.tasks[task_id] = (task,args,kargs,period,epoch,runs)


    def _run(self,time):
        """ Exec tasks that have reached time to run. *time* is the current
        time. """

        # update time
        self._set(time)

        # run each task that has reached its run time
        runned = 0
        for self.task_id,self.truntime in self.torun:
            if self.truntime <= self.runtime:
                task,args,kargs,period,epoch,runs = self.tasks[self.task_id]
                if args:
                    if kargs:
                        task(*args,**kargs)
                    else:
                        task(*args)
                else:
                    if kargs:
                        task(**kargs)
                    else:
                        task()
                
                # if required, do runs count down
                if runs > 0:
                    runs = runs - 1
                    self.tasks[self.task_id] = task,args,kargs,period,epoch,runs
                # if task has a next run, queue it.
                if runs:
                    next_run = self.runtime + period  \
                        - mt.fmod(self.runtime - epoch,period)
                    self.torun.append((self.task_id,next_run))
                runned = runned + 1
            else:
                break

        # sort future runs by run ascending time
        if self.torun:
            self.torun = sorted(self.torun[runned:],key=op.itemgetter(1))


    def _set(self,new_time):
        """ Update time. *new_time*, the new time value. """

        # save new_time
        self.time = new_time

        # if time is defined, compute derivative times.
        if not self.time is None:
            self.runtime = self.time - mt.fmod(self.time,self.tick)
            self.second = mt.floor(self.time)
            self.minute = self.time - mt.fmod(self.time,60.)


    def task_data(self):
        """ Return current task data.

        Return pattern (**runtime**, **id**)

          **runtime**: float, the nominal task run time.

          **id**: integer, the task identifier, it is the order of registration
          starting from zero. """

        return self.task_id, self.truntime

#### END
