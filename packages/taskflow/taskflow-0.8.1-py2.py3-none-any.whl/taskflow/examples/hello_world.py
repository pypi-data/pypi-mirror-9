# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os
import sys

logging.basicConfig(level=logging.ERROR)

top_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.pardir,
                                       os.pardir))
sys.path.insert(0, top_dir)

from taskflow import engines
from taskflow.patterns import linear_flow as lf
from taskflow.patterns import unordered_flow as uf
from taskflow import task
from taskflow.types import futures
from taskflow.utils import eventlet_utils


# INTRO: This is the defacto hello world equivalent for taskflow; it shows how
# an overly simplistic workflow can be created that runs using different
# engines using different styles of execution (all can be used to run in
# parallel if a workflow is provided that is parallelizable).

class PrinterTask(task.Task):
    def __init__(self, name, show_name=True, inject=None):
        super(PrinterTask, self).__init__(name, inject=inject)
        self._show_name = show_name

    def execute(self, output):
        if self._show_name:
            print("%s: %s" % (self.name, output))
        else:
            print(output)


# This will be the work that we want done, which for this example is just to
# print 'hello world' (like a song) using different tasks and different
# execution models.
song = lf.Flow("beats")

# Unordered flows when ran can be ran in parallel; and a chorus is everyone
# singing at once of course!
hi_chorus = uf.Flow('hello')
world_chorus = uf.Flow('world')
for (name, hello, world) in [('bob', 'hello', 'world'),
                             ('joe', 'hellooo', 'worllllld'),
                             ('sue', "helloooooo!", 'wooorllld!')]:
    hi_chorus.add(PrinterTask("%s@hello" % name,
                              # This will show up to the execute() method of
                              # the task as the argument named 'output' (which
                              # will allow us to print the character we want).
                              inject={'output': hello}))
    world_chorus.add(PrinterTask("%s@world" % name,
                                 inject={'output': world}))

# The composition starts with the conductor and then runs in sequence with
# the chorus running in parallel, but no matter what the 'hello' chorus must
# always run before the 'world' chorus (otherwise the world will fall apart).
song.add(PrinterTask("conductor@begin",
                     show_name=False, inject={'output': "*ding*"}),
         hi_chorus,
         world_chorus,
         PrinterTask("conductor@end",
                     show_name=False, inject={'output': "*dong*"}))

# Run in parallel using eventlet green threads...
if eventlet_utils.EVENTLET_AVAILABLE:
    with futures.GreenThreadPoolExecutor() as executor:
        e = engines.load(song, executor=executor, engine='parallel')
        e.run()


# Run in parallel using real threads...
with futures.ThreadPoolExecutor(max_workers=1) as executor:
    e = engines.load(song, executor=executor, engine='parallel')
    e.run()


# Run in parallel using external processes...
with futures.ProcessPoolExecutor(max_workers=1) as executor:
    e = engines.load(song, executor=executor, engine='parallel')
    e.run()


# Run serially (aka, if the workflow could have been ran in parallel, it will
# not be when ran in this mode)...
e = engines.load(song, engine='serial')
e.run()
