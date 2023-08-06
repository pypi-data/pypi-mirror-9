==============
Usage examples
==============

This simple example is based on the the execution of 3 tasks. First task is run
every 5 seconds, at second beginning, forever. The second and the third tasks
are run every second, at the middle of second, forever.
Each task printouts its task id, nominal runtime and delay of real runtime
from nominal runtime.
Since all these tasks make the same output, they all can be inplemented by only
one function, the "task" function.

.. literalinclude:: ../examples/example.py
    :linenos:
    :language: python
    :lines: 30-

This an excerpt from example output. Task with 5 second period has id=0.
Tasks with 1 second period have respectively id=1 and id=2.
 
.. literalinclude:: ../examples/example.out
    :linenos:
