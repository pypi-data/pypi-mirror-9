=====================
 Apycot architecture
=====================

Apycot is designed to be an extensible test automation tool usable for continuous
integration and continuous testing.

It can fetch source code from version-controlled repositories (like SVN or Hg),
run tests, then store the results and generate various reports from the data
collected. Once the tests are configured, users can be notified in realtime
when the status of a test changes or get a periodic report about the health
of the projects their work on.

.. image:: doc/images/apycot_processes.png

Cubicweb instances contain environment and test configurations, as well as test
execution information that may be used to build useful reports.

Once configured, you can explicitly queue a task (eg run tests for a
configuration) through a test configuration page. To get actual CI you'll have to
`automate this`_.

When a task is queued through `apycotclient` or the web user interface, an
apycot bot will get tasked with it:

* the bot will retrieve the configuration from the instance hosting it

* the bot will execute the task (setup environmenent, run tests) and 
  store the output in the instance from which it got the configuration.

---------------
Testing Process
---------------

Apycot builds upon the narval cube and bot. The process of running a test in
apycot is based on the way narval runs tests and looks like:

.. aafig::

     Narval bot server                    Web app server

   +-----+  +----------+                +----------------+
   | bot |  | run-plan |                | apycot web app |
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
      X          |                               X
      X          X fire setup transition (POST)  X
      X          X------------------------------>X
      X          X<------------------------------X
      X          |                               X
      X          X execfile(recipe)              X
      X      ____|_______________________________X____
      X      | for each checker |                X   | 
      X      |_________________/                 X   |
      X      |   |                               X   |
      X      |   X create                        X   |
      X      |   X a CheckResult entity          X   |
      X      |   X (POST)                        X   |
      X      |   X------------------------------>X   |
      X      |   X<------------------------------X   |
      X      |   X      CheckResult cwuri        X   |
      X      |   X                               X   |
      X      |   X  refresh log_file (POST)      X   |
      X      |   X------------------------------>X   |
      X      |   X                               X   |
      X      |   X run(checker)                  X   |
      X      |   X                               X   |
      X      |   X  refresh log_file (POST)      X   |
      X      |   X------------------------------>X   |
      X      |   X                               X   |
      X      |   X  set status of                X   |
      X      |   X  CheckResults (POST)          X   |
      X      |   X------------------------------>X   |
      X      |___X_______________________________X___|
      X          X                               X 
      X          X  refresh log_file (POST)      X
      X          X------------------------------>X
      X          X                               X 
      X          X  set status of                X
      X          X  TestExecution (POST)         X
      X          X------------------------------>X
      X          X<------------------------------X
      X          X                               X
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

The `narval-plan` sub-process retrieves the job's description and changes its
workflow state, prepares the job environment (checkout, dependencies...) and,
for each checker in the job, runs the checker and transmits all the results to
a specifically-created CheckResult entity on the webapp. Finally, the
narval-plan log is uploaded to the web application.
