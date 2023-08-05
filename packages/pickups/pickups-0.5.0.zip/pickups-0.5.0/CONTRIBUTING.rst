.. _contributing:

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given. 

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/maiksensi/pickups/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

pickups could always use more documentation, whether as part of the
official pickups docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/maiksensi/pickup/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `pickups` for
local development.

1. Fork_ the `pickups` repo on GitHub (`Howto Fork A Repo <https://help.github.com/articles/fork-a-repo/>`_).
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/pickup.git

3. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

Now you can make your changes locally.

4. When you're done making changes, check that your changes pass style and unit
   tests, including testing other Python versions with tox::

    $ tox

To get tox, just pip install it.

5. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

.. _Fork: https://github.com/maiksensi/pickups/fork

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. Your tests should have reach coverage of 95% or higher.
3. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
4. Follow the `Python Styleguide <https://www.python.org/dev/peps/pep-0008/>`_
   with the exception that lines can be up to ``120`` characters long.
5. The pull request should work for Python 2.7, and 3.4, and for PyPy.
   Check https://travis-ci.org/maiksensi/pickups
   under pull requests for active pull requests or run the ``tox`` command and
   make sure that the tests pass for all supported Python versions.


Tips
----

To run a subset of tests::

	 $ py.test test/test_pickups.py

Github's documentation on how to create a pull-request can be found in the
`User Documentation <https://help.github.com/articles/creating-a-pull-request/>`_.
