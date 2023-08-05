========
venvctrl
========

*Python API for interacting with virtual environments.*

Why?
====

The only real interface provided by a virtual environment is the CLI. This
package wraps the command line tools to provide a more friendly programmatic
interface.

Creating A Venv
===============

.. code-block:: python

    from venvctrl import api

    api.VirtualEnvironment('/some/path/here').create()


Installing Packages
===================

.. code-block:: python

    from venvctrl import api

    venv = api.VirtualEnvironment('/some/existing/venv')
    if not venv.has_package('venvctrl'):

        venv.install_package('venvctrl')

    else:

        venv.uninstall_package('venvctrl')


Moving A Venv
=============

.. code-block:: python

    from venvctrl import api

    venv = api.VirtualEnvironment('/some/existing/venv')
    venv.move('/some/new/path')

Alternatively, use the CLI.

.. code-block:: bash

    venvctrl-relocate \
        --source=/some/existing/venv \
        --destination=/some/new/path \
        --move

License
=======

::

    (MIT License)

    Copyright (C) 2015 Kevin Conway

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to
    deal in the Software without restriction, including without limitation the
    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.


Contributing
============

All contributions to this project are protected under the agreement found in
the `CONTRIBUTING` file. All contributors should read the agreement but, as
a summary::

    You give us the rights to maintain and distribute your code and we promise
    to maintain an open source distribution of anything you contribute.
