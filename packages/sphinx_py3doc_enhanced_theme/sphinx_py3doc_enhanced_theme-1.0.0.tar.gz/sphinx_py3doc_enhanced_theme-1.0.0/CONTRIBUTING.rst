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

Report bugs at https://github.com/ionelmc/sphinx-py3doc-enhanced-theme/issues.

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

Enhanced theme based on py3 documentation's theme could always use more documentation, whether as part of the
official Enhanced theme based on py3 documentation's theme docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/ionelmc/sphinx-py3doc-enhanced-theme/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `sphinx-py3doc-enhanced-theme` for local development.

1. Fork the `sphinx-py3doc-enhanced-theme` repo on GitHub.
2. Clone your fork locally::

    git clone git@github.com:your_name_here/sphinx-py3doc-enhanced-theme.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

4. When you're done making changes, run all the checks, doc builder and spell checker with `tox <http://tox.readthedocs.org/en/latest/install.html>`_::

    tox

5. Commit your changes and push your branch to GitHub::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

6. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include passing tests.
2. If the pull request adds functionality, the docs should be updated. Make sure that the new code has docstrings and
   it's included in the reference. Add a note to `CHANGELOG.rst` about the changes.
3. Run the tests with ``tox``. If you don't have all the necessary python versions available locally you can take a look
   at https://travis-ci.org/ionelmc/sphinx-py3doc-enhanced-theme/pull_requests and make sure
   everything passes.

Tips
----

To run a subset of tests::

    tox -e envname -- pytest -k test_myfeature