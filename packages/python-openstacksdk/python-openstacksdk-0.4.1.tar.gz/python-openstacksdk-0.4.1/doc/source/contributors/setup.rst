Creating a Development Environment
==================================

Required Tools
--------------

Python
******

As the OpenStack SDK is developed in Python, you will need at least one
version of Python installed. It is strongly preferred that you have at least
one of version 2 and one of version 3 so that your tests are run against both.
Our continuous integration system runs against several versions, so ultimately
we will have the proper test coverage, but having multiple versions locally
results in less time spent in code review when changes unexpectedly break
other versions.

Python can be downloaded from https://www.python.org/downloads.

virtualenv
**********

In order to isolate our development environment from the system-based Python
installation, we use `virtualenv <https://virtualenv.pypa.io/en/latest/>`_.
This allows us to install all of our necessary dependencies without
interfering with anything else, and preventing others from interfering with us.
Virtualenv must be installed on your system in order to use it, and it can be
had from PyPI, via pip, as follows. Note that you may need to run this
as an administrator in some situations.::

   $ apt-get install python-virtualenv  # Debian based platforms
   $ yum install python-virtualenv      # Red Hat based platforms
   $ pip install virtualenv             # Mac OS X and other platforms

You can create a virtualenv in any location. A common usage is to store all
of your virtualenvs in the same place, such as under your home directory.
To create a virtualenv for the default Python, likely a version 2, run
the following::

   $ virtualenv $HOME/envs/sdk

To create an environment for a different version, such as Python 3, run
the following::

   $ virtualenv -p python3.4 $HOME/envs/sdk3

When you want to enable your environment so that you can develop inside of it,
you *activate* it. To activate an environment, run the /bin/activate
script inside of it, like the following::

   $ source $HOME/envs/sdk3/bin/activate
   (sdk3)$

Once you are activated, you will see the environment name in front of your
command prompt. In order to exit that environment, run the ``deactivate``
command.

tox
***

We use `tox <https://tox.readthedocs.org/en/latest/>`_ as our test runner,
which allows us to run the same test commands against multiple versions
of Python. Inside any of the virtualenvs you use for working on the SDK,
run the following to install ``tox`` into it.::

   (sdk3)$ pip install tox

Git
***

The source of the OpenStack SDK is stored in Git. In order to work with our
source repository, you must have Git installed on your system. If your
system has a package manager, it can likely be had from there. If not,
you can find downloads or the source at http://git-scm.com.

Getting the Source Code
-----------------------

.. TODO(briancurtin): We should try and distill the following document
   into the minimally necessary parts to include directly in this section.
   I've talked to several people who are discouraged by that large of a
   document to go through before even getting into the project they want
   to work on. I don't want that to happen to us because we have the potential
   to be more public facing than a lot of other projects.

.. note:: Before checking out the code, please read the OpenStack
          `Developer's Guide <http://docs.openstack.org/infra/manual/developers.html>`_
          for details on how to use the continuous integration and code
          review systems that we use.

The canonical Git repository is hosted on openstack.org at
http://git.openstack.org/cgit/stackforge/python-openstacksdk/, with a
mirror on GitHub at https://github.com/stackforge/python-openstacksdk.
Because of how Git works, you can create a local clone from either of those,
or your own personal fork.::

   (sdk3)$ git clone git@github.com:briancurtin/python-openstacksdk.git
   (sdk3)$ cd python-openstacksdk

Installing Dependencies
-----------------------

In order to work with the SDK locally, such as in the interactive interpreter
or to run example scripts, you need to install the project's dependencies.::

   (sdk3)$ pip install -r requirements.txt

After the downloads and installs are complete, you'll have a fully functional
environment to use the SDK in. This step installs the following dependencies.

* `oslo.utils <https://pypi.python.org/pypi/oslo.utils>`_, which we use
  for its ``timeutils`` module when calculating if or when authentication
  tokens are considered expired.
* `pbr <https://pypi.python.org/pypi/pbr>`_, or the Python Build
  Reasonableness project. pbr injects a set of common defaults which are used
  throughout the OpenStack project.
* `requests <https://pypi.python.org/pypi/requests>`_, which we use in the
  :class:`~openstack.transport.Transport` class to handle HTTP requests and
  responses.
* `six <https://pypi.python.org/pypi/six>`_, which we use for compatibility
  across Python 2 and 3.
* `stevedore <https://pypi.python.org/pypi/stevedore>`_, which we use for
  working with plugins. stevedore builds on setuptools ``entry_points``.

Running the Tests
-----------------

In order to run the entire test suite, simply run the ``tox`` command inside
of your source checkout. This will attempt to run every test command listed
inside of ``tox.ini``, which includes Python 2.6, 2.7, 3.3, 3.4, PyPy, and
a PEP 8 check. You should run the full test suite on all versions before
submitting changes for review in order to avoid unexpected failures in
the continuous integration system.::

   (sdk3)$ tox
   ...
   py33: commands succeeded
   py34: commands succeeded
   py26: commands succeeded
   py27: commands succeeded
   pypy: commands succeeded
   pep8: commands succeeded
   congratulations :)

During development, it may be more convenient to run a subset of the tests
to keep test time to a minimum. You can choose to run the tests only on one
version. A step further is to run only the tests you are working on.::

   (sdk3)$ tox -e py34                # Run run the tests on Python 3.4
   (sdk3)$ tox -e py34 TestContainer  # Run only the TestContainer tests on 3.4

Building the Documentation
--------------------------

Our documentation is written in reStructured Text and is built using
Sphinx. A ``docs`` command is availble in our ``tox.ini``, allowing you
to build the documentation like you'd run tests. The ``docs`` command is
not evaluated by default.::

   (sdk3)$ tox -e docs

That command will cause the documentation, which lives in the ``docs`` folder,
to be built. HTML output is the most commonly referenced, which is located
in ``docs/build/html``.
