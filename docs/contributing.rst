Contributing
============


Installing
----------
See: :doc:`Getting started <getting_started>`


Testing
-------
See: :doc:`Testing <testing>`


Guidelines for Contributing
---------------------------

Please use the following guidelines when updating:

1.  Add changes to the ``CHANGES.rst`` file found within the top folder
    of the repository.

2.  Add your name to the ``AUTHORS.rst`` file found within the top
    folder of the repository.

3.  There are two main, long-running branches:

    * ``develop`` - the unstable, integration branch
    * ``master`` - the stable, deployable branch

4.  The use of `git-flow`_ as a process is encouraged.  In addition to
    the branches mentioned above, the following branches are used.

    * ``feature`` - ephemeral branch for feature changes and bug fixes
    * ``hotfix`` - ephemeral branch for immediate changes to ``master``
    * ``release`` - QA branch for developing pre-releases and ultimately
                    updating ``master``

5.  Please update and run tests.  Check Coverage:  80% is a good number
    to strive for.

6.  Releases happen on an as-needed basis.


.. _git-flow: http://nvie.com/posts/a-successful-git-branching-model/