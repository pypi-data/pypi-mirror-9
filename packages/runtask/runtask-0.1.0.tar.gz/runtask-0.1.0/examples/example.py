#!/usr/bin/python
# .+
# .context    : RunTask, coherent time task scheduler
# .title      : example
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

import runtask as rt           # task scheduler
import time as tm              # time interface

# set up the time scheduler
scheduler = rt.RunTask(tick=0.1)

# a task printing run time
def task(scheduler):
    now = tm.time()
    task_id, runtime = scheduler.task_data()
    print 'task',task_id,runtime,now-runtime

# task every 5 seconds, epoch aligned, forever
scheduler.task(task,[scheduler],{},5.,0.0,-1)

# two tasks every seconds, half second aligned, forever
scheduler.task(task,[scheduler],{},1.,0.5,-1)
scheduler.task(task,[scheduler],{},1.,0.5,-1)

scheduler.start()

#### END
