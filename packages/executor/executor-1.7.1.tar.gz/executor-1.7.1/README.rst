executor: Programmer friendly subprocess wrapper
================================================

.. image:: https://travis-ci.org/xolox/python-executor.svg?branch=master
   :target: https://travis-ci.org/xolox/python-executor

.. image:: https://coveralls.io/repos/xolox/python-executor/badge.png?branch=master
   :target: https://coveralls.io/r/xolox/python-executor?branch=master

The ``execute()`` function in the ``executor`` package/module is a simple
wrapper for Python's subprocess_ module that makes it very easy to handle
subprocesses on UNIX systems with proper escaping of arguments and error
checking. It's currently tested on Python 2.6, 2.7 and 3.4. For usage
instructions please refer to the documentation_.

Examples of usage
-----------------

Below are some examples of how versatile the ``execute()`` function is.

Checking status codes
~~~~~~~~~~~~~~~~~~~~~

The status code of the subprocess is returned as a boolean:

>>> from executor import execute
>>> execute('true')
True

If a subprocess exits with a nonzero status code an exception is raised,
this makes it easy to do the right thing (i.e. check the status codes of
all subprocesses without having to write a lot of repetitive code):

>>> execute('false')
Traceback (most recent call last):
  File "executor/__init__.py", line 79, in execute
    raise ExternalCommandFailed, msg % (shell.returncode, command)
executor.ExternalCommandFailed: External command failed with exit code 1! (command: false)

The exceptions raised by the ``execute()`` functions expose ``command`` and
``returncode`` attributes. If you know a command is likely to exit with a
nonzero status code and you want ``execute()`` to simply return a boolean you
can do this:

>>> execute('false', check=False)
False

Getting output
~~~~~~~~~~~~~~

Getting the output of subprocesses is really easy as well:

>>> execute('hostname', capture=True)
'peter-macbook'

Running commands as root
~~~~~~~~~~~~~~~~~~~~~~~~

It's also very easy to execute commands with super user privileges:

>>> execute('echo test > /etc/hostname', sudo=True)
[sudo] password for peter: **********
True
>>> execute('hostname', capture=True)
'test'

Enabling logging
~~~~~~~~~~~~~~~~

If you're wondering how prefixing the above command with ``sudo`` would
end up being helpful, here's how it works:

>>> import logging
>>> logging.basicConfig()
>>> logging.getLogger().setLevel(logging.DEBUG)
>>> execute('echo peter-macbook > /etc/hostname', sudo=True)
DEBUG:executor:Executing external command: sudo bash -c 'echo peter-macbook > /etc/hostname'

Contact
-------

The latest version of ``executor`` is available on PyPI_ and GitHub_. The
documentation is hosted on `Read the Docs`_. For bug reports please create an
issue on GitHub_. If you have questions, suggestions, etc. feel free to send me
an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2015 Peter Odding.

.. External references:
.. _documentation: https://executor.readthedocs.org
.. _GitHub: https://github.com/xolox/python-executor
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPI: https://pypi.python.org/pypi/executor
.. _Read the Docs: https://executor.readthedocs.org
.. _subprocess: https://docs.python.org/2/library/subprocess.html
