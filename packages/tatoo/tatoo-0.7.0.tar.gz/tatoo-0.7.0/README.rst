.. image:: https://badge.fury.io/py/tatoo.png
    :target: http://badge.fury.io/py/tatoo

.. image:: https://travis-ci.org/malinoff/tatoo.svg?branch=develop&label=Travis
    :target: https://travis-ci.org/malinoff/tatoo

.. image:: https://ci.appveyor.com/api/projects/status/github/malinoff/tatoo?svg=true&branch=develop&passingText=Appveyor%20|%20passing&pendingText=Appveyor%20|%20pending&failingText=Appveyor%20|%20failing
    :target: https://ci.appveyor.com/project/malinoff/tatoo/branch/develop

tatoo - task toolkit
====================

Tatoo is python task toolkit, intended to be small and simple, but
powerful and extensible. Out of the box it allows you to programmatically
execute tasks on the local machine::

    >>> from tatoo import Environment
    >>> env = Environment()
    >>> @env.task
    >>> def hello():
    ...     print('Hello, world!')
    ...
    >>> hello.apply()
    Hello, world!

It can be use as a replacement for tools like ``Make`` (a command-line
interface is provided via extensions), but it was developed with
``Celery``'s features in mind, so once there will be extensions for
remote task execution, daemonization and others.

Documentation can be found on `read the docs
<http://tatoo.readthedocs.org/en/latest/>`_.

It works under Python 2.6, 2.7, 3.3+ and Pypy (Pypy3 is not yet
supported) on Linux, OSX and Windows. This
ensured on each commit continiously using
`TravisCI <https://travis-ci.org/malinoff/tatoo>`_ (Linux & OSX) and
`Appveyor <https://ci.appveyor.com/project/malinoff/tatoo/>`_ (Windows).
