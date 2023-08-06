=====================
 Narval architecture
=====================

The standard process of a narval test session looks like:

.. aafig::

     Narval bot server                    Web app server

   +-----+  +----------+                +----------------+
   | bot |  | run-plan |                | narval web app |
   +--+--+  +----+-----+                +--------+-------+
      |          |                               |
      |          |                               |
      X poll (HTTP GET)                          X
      X----------------------------------------->X
      X<-----------------------------------------X
      X list of pending plans (eids)             X
      X          |                               X
      X spawn (narval run-plan plan-uri)         X
      X--------->X                               X
      X          X get plan description (GET)    X
      X          X------------------------------>X
      X          X<------------------------------X
      X          X   plan description (recipe)   X
      X          X                               X
      X          X fire start transition (POST)  X
      X          X------------------------------>X
      X          X<------------------------------X
      X          X                               X
      X          X execfile(recipe)              X
      X          X                               X
      X          X  fire end transition (POST)   X
      X          X------------------------------>X
      X  stdout  X                               X
      X<---------X                               X
      X<---------X                               X
      X  stderr  X                               X
      X          |                               X
      X          |    POST execution_log (POST)  X
      X----------------------------------------->X
      X                                          X
      X          |      poll (HTTP GET)          X
      X----------------------------------------->X
      X<-----------------------------------------X
      X          |                               X
      X          |                               X




The bot is responsible for checking if there are pending tasks,
spawning a sub-processes for each task, and monitoring this latter
sub-process execution (resources limits, crash, etc.).

The `narval-plan` sub-process is responsible for retrieving the job's
description and changing its workflow state, execute the corresponding
job and uploading the produced log files on the web application.
