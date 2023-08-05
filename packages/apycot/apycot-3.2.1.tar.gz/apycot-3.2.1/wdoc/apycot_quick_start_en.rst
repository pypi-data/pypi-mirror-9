====================
 Apycot Quick Start
====================

--------
Overview
--------

Apycot is designed to be an extensible test automation tool usable for
continuous integration and continuous testing. It is a CubicWeb-based
application extending the Narval framework. It adds the notion of preprocessors
and checkers to Narval. The preprocessors are used mainly to checkout
version-controlled repositories and setup a test environment while the checkers
correspond to specific checks (pycoverage, pytest, pylint...).

Other major differences with respect to Narval include the use of TestExecution
and CheckResults instead of Plans to store the results and the organisation of
test environments through ProjectEnvironments and TestConfigs.

The Apycot framework, like Narval is split between:

- a Web application used for storing, presenting and accessing the test results;
- a bot regularly polling the web application using http, running the tests
  when necessary and transmitting back the results to the Web application.

Both parts can be installed on the same machine or on different machines able
to communicate via HTTP. Please read the Narval documentation before installing
Apycot.

-----------
Definitions
-----------

* A **repository** is a version-controlled sources (VCS) database, like SVN or
  Hg.

* A **preprocessor** allows a specific construction / installation step
  required to build a test environment.  Example preprocessors: 'setup_install'
  to install a package by using `python setup.py install`, 'make' call the
  `make` command...

* A **check** is a single functional test which may be applied to test a
  package. A **checker** is the object applying this functional test.  Example
  checks: 'pyunit' to start python unittest, 'pylint' to start pylint...

---------
Narvalbot
---------

Installation
============

In addition to what is described in the Narval documentation, you need to install
the additional ``narval-apycot`` package (it contains the additional checkers and
preprocessors used by apycot).

.. sourcecode:: bash

  apt-get install narval-bot narval-apycot

Configuration
=============

Follow the Narval bot configuration documentation to configure the Narval bot.

---------------
Cubicweb-apycot
---------------

Installation
============

To install a complete Apycot environment, you need to install the following packages:

.. sourcecode:: bash

  apt-get install cubicweb-apycot cubicweb-ctl

Creating an Apycot instance
===========================

.. sourcecode:: bash

  cubicweb-ctl create apycot myapycot


You can then launch the CubicWeb instance:

.. sourcecode:: bash

  cubicweb-ctl start -D myapycot

Make sure the bot manages to connect to the instance by looking at the logs in `/var/log/narval/narval.log`. If you see something like::

  2014-01-15 20:20:40 - (narval.bot) INFO: get pending plan from narval
  2014-01-15 20:20:40 - (requests.packages.urllib3.connectionpool) INFO: Starting new HTTP connection (1): crater2.logilab.fr

it means everything is working as expected. If the Narval bot cannot connect, you will see this instead::

  Traceback (most recent call last):
    File "/usr/lib/pymodules/python2.7/narvalbot/server.py", line 107, in _loop
      for plandata in self.config.cnxh(instance_id).pending_plans():
    File "/usr/lib/pymodules/python2.7/narvalbot/__init__.py", line 222, in pending_plans
      '?vid=narval.pending-plans'))
    File "/usr/lib/pymodules/python2.7/narvalbot/__init__.py", line 182, in http_get
      return self.http_post(url, method='get')
    File "/usr/lib/pymodules/python2.7/narvalbot/__init__.py", line 192, in http_post
      self.connect()
    File "/usr/lib/pymodules/python2.7/narvalbot/__init__.py", line 212, in connect
      '?__login=%s&__password=%s' % (user, password)))
    File "/usr/lib/pymodules/python2.7/narvalbot/__init__.py", line 247, in open
      return self.opener.open(*args, **kwargs)
    File "/usr/lib/python2.7/urllib2.py", line 401, in open
      response = self._open(req, data)
    File "/usr/lib/python2.7/urllib2.py", line 419, in _open
      '_open', req)
    File "/usr/lib/python2.7/urllib2.py", line 379, in _call_chain
      result = func(*args)
    File "/usr/lib/python2.7/urllib2.py", line 1211, in http_open
      return self.do_open(httplib.HTTPConnection, req)
    File "/usr/lib/python2.7/urllib2.py", line 1181, in do_open
      raise URLError(err)
  URLError: <urlopen error [Errno 111] Connection refused>

Setting up a test environment
=============================

We first describe the entity types added by Apycot and then provide a complete
setup procedure.

Creating a project environment (ProjectEnvironment)
---------------------------------------------------

To setup a ProjectEnvironment, you need to specify:

- the ProjectEnvironment name
- the configuration variables. These variables are available in the
  checkers and preprocessors in the options object. For example ::

  install=python_setup
  pycoverage=True
  extra_argument=['-m', 'Corp']
  test_dirs=['tests']
  test_prefixes=['test_','unittest_']
  pylint_threshold=70
  pylintrc='~/.pylintrc'
  coverage_threshold=0.7
  keep_test_dir=True
  archive=False
  required=False
  verbose=True

- the environment variables. These variables will be available in the
  shell for the preprocessors and checkers. For example::

  NO_SETUPTOOLS=1
  DISPLAY=:1.0

Usually, when checkers or preprocessors fail, or crash, some of these variables
are incorrect or missing.

Creating a test configuration (TestConfig)
------------------------------------------

Usually, a recipe requires at least a TestConfig. This configuration
contains all the necessary information to run the tests.

To setup a TestConfig, you need to specify:

- the TestConfig name
- the launching mode ("manual" by default)
- the way dependent project environments are tested when the TestConfig
  is modified; can be "yes" (thus you lauch the tests for these project
  environments), "no" (thus, you dont lauch the tests), and "inherited" (the
  value is set elsewhere).
- the configuration variables and environment variables. These are similar to
  the configuration variables found in ProjectEnvironment instances.
- the recipe associated to the TestConfig. This recipe will be launched
  by the narval instance when this configuration will be used.
- the "refinement of" specifies the parent TestConfig. The current TestConfig
  will inherit all the attributes and variables from the parent TestConfig.

To run tests you must link the TestConfig to a ProjectEnvironment and specify a
recipe. Make sure the options necessary for each checker and preprocessor are
availalbe in either the ProjectEnvironment or the TestConfig.

Creating a repository
---------------------

The Repository is a proxy to a VCS repository holding the project to be tested,
e.g. Mercurial.

To setup a Repository, you need to specify:

- the type of the VCS handling the Repository;
- the path to the Repository.

Make sure the Repository can be accessed by both the Apycot Web application and
the Narval bot instance.

In the "files" tab you can find all the files in the current revision, whereas
in the "revisions" tabs you have a table with all revisions known to the
Repository.

Full setup procedure
--------------------

Make sure the cubicweb instance running Apycot and the Narval bot instance are
both installed, configured (as shown above and in the Narval documentation) and
able to communicate (see their respective install procedures).

1. Setup a Repository for the project
2. Create a TestConfig for each recipe you want to be able to run.
   - make sure the correct recipe is selected for each TestConfig.
   - make sure to fill-in the necessary options (``install=python_setup`` is
     usually mandatory for Python recipes).
3. Setup a ProjectEnvironment for the project
   - link the ProjectEnvironment to the previously created Repository
   - link the ProjectEnvironment to all the necessary TestConfig instances.
4. From the ProjectEnvironment view in cubicweb, manually launch the tests and
   watch the results appear on you display (if you do not see the option to
   launch tests, make sure you are logged in and have the necessary
   authorizations).

Troubleshooting
---------------

The Narval bot never gets the plan and the interval between the bot's polls is
too long:

- the interval can be modified in `/etc/narval/narval-cw-sources.ini` to add
  the ``poll-delay`` argument::

  [narval]
  url=http://instance-name.fr:10003/
  token_id=token name
  secret=generated secret
  poll-delay=5

The checkers crash but the project tests are fine, the project is not installed
correctly:

- make sure no configuration and environment variables are missing or wrongly
  set.
- check the paths used by Narval bot are writable and free space is available
  on the disk.
