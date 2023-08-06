==============
Phantom Scheduler
==============

Phantom scheduler used to administer the job submission to clusters.

"With great power comes great responsibility" -- Uncle Ben

This program runs a scheduler and a number of children that keep submitting jobs to a cluster queue.

It is particularly useful when one has many short jobs which cannot be submitted all at once. This permits not to lose the priority in the queue.

Installation
============

You can install the ``phantom_scheduler`` using:

    $ pip install phantom_scheduler

