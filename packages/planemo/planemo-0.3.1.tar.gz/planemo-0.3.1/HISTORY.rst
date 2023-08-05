.. :changelog:

History
-------

---------------------
0.3.0 (2015-02-13)
---------------------

 * Add option (``-r``) to the ``shed_upload`` command to recursively upload
   subdirectories (thanks to Eric Rasche). `Pull Request 68`_
 * Fix diff formatting in test reports (thanks to Eric Rasche).
   `Pull Request 63`_
 * Grab updated test database to speed up testing (thanks to approach from
   Eric Rasche and Dannon Baker). `Issue 61`_, dff4f33_
 * Fix test data command-line argument name (was ``test-data`` now it is
   ``test_data``). 834bfb2_
 * Use ``tool_data_table_conf.xml.sample`` file if
   ``tool_data_table_conf.xml.test`` is unavailable. Should allow some
  new tools to be tested without modifying Galaxy's global
  ``tool_data_table_conf.xml`` file. ac4f828_

---------------------
0.2.0 (2015-01-13)
---------------------

* Improvements to way Planemo loads its own copy of Galaxy modules to prevent
  various conflicts when launching Galaxy from Planemo. `Pull Request 56`_
* Allow setting various test output options in ``~/.planemo.yml`` and disabling
  JSON output. 21bb463_
* More experimental Brew and Tool Shed options that should not be considered
  part of Planemo's stable API. See bit.ly/gxbrew1 for more details.
* Fix ``project_init`` for BSD tar (thanks to Nitesh Turaga for the bug
  report.) a4110a8_
* Documentation fixes for tool linting command (thanks to Nicola Soranzo).
  `Pull Request 51`_

---------------------
0.1.0 (2014-12-16)
---------------------

* Moved repository URL to https://github.com/galaxyproject/planemo.
* Support for publishing to the Tool Shed. `Pull Request 6`_
* Support for producing diffs (``shed_diff``) between local repositories and
  the Tool Shed (based on scripts by Peter Cock). `Pull Request 33`_
* Use tool's local test data when available - add option for configuring
  ``test-data`` target. `Pull Request 1`_
* Support for testing tool features dependent on cached data. 44de95c_
* Support for generating XUnit tool test reports. 82e8b1f_
* Prettier HTML reports for tool tests. 05cc9f4_
* Implement ``share_test`` command for embedding test result links in pull
  requests. `Pull Request 40`_
* Fix for properly resolving links during Tool Shed publishing (thanks to Dave
  Bouvier). `Pull Request 29`_
* Fix for citation linter (thanks to Michael Crusoe for the bug report). af39061_
* Fix tool scanning for tool files with fewer than 10 lines (thanks to Dan
  Blankenberg). a2c13e4_
* Automate more of Travis CI testing so the scripts added to tool repository
  can be smaller. 20a8680_
* Documentation fixes for Travis CI (thanks to Peter Cock). `Pull Request 22`_,
  `Pull Request 23`_
* Various documentation fixes (thanks to Martin Čech). 36f7cb11_, b9232e55_
* Various smaller fixes for Docker support, tool linting, and documentation.

---------------------
0.0.1 (2014-10-04)
---------------------

* Initial work on the project - commands for testing, linting, serving Galaxy
  tools - and more experimental features involving Docker and Homebrew. 7d07782_

.. _Pull Request 68: https://github.com/galaxyproject/planemo/pull/68
.. _Issue 61: https://github.com/galaxyproject/planemo/issues/61
.. _Pull Request 63: https://github.com/galaxyproject/planemo/pull/63
.. _Pull Request 56: https://github.com/galaxyproject/planemo/pull/56
.. _Pull Request 51: https://github.com/galaxyproject/planemo/pull/51
.. _Pull Request 40: https://github.com/galaxyproject/planemo/pull/40
.. _Pull Request 29: https://github.com/galaxyproject/planemo/pull/29
.. _Pull Request 22: https://github.com/galaxyproject/planemo/pull/22
.. _Pull Request 23: https://github.com/galaxyproject/planemo/pull/23
.. _Pull Request 33: https://github.com/galaxyproject/planemo/pull/33
.. _Pull Request 6: https://github.com/galaxyproject/planemo/pull/6
.. _Pull Request 1: https://github.com/galaxyproject/planemo/pull/1
.. _ac4f828: https://github.com/galaxyproject/planemo/ac4f82898f7006799142503a33c3978428660ce7
.. _834bfb2: https://github.com/galaxyproject/planemo/commit/834bfb2929d367892a3abe9c0b88d5a0277d7905
.. _dff4f33: https://github.com/galaxyproject/planemo/commit/dff4f33c750a8dbe651c38e149a26dd42e706a82
.. _a4110a8: https://github.com/galaxyproject/planemo/commit/a4110a85a770988e5cd3c31ccc9475717897d59c
.. _21bb463: https://github.com/galaxyproject/planemo/commit/21bb463ad6c321bcb669603049a5e89a69766ad9
.. _af39061: https://github.com/galaxyproject/planemo/commit/af390612004dab636d8696839bb723d39f97c85d
.. _20a8680: https://github.com/galaxyproject/planemo/commit/20a86807cb7ea87db2dbc0197ae08a40df3ab2bc
.. _44de95c: https://github.com/galaxyproject/planemo/commit/44de95c0d7087a5822941959f9a062f6382e329b
.. _82e8b1f: https://github.com/galaxyproject/planemo/commit/82e8b1f17eae526aeb341cb4fffb8d09d73bb419
.. _05cc9f4: https://github.com/galaxyproject/planemo/commit/05cc9f485ee87bc344e3f43bb1cfd025a16a6247
.. _32c6e7f: https://github.com/galaxyproject/planemo/commit/32c6e7f78bb8f04d27615cfd8948b0b89f27b4e6
.. _7d07782: https://github.com/galaxyproject/planemo/commit/7d077828559c9c9c352ac814f9e3b86b1b3a2a9f
.. _a2c13e4: https://github.com/galaxyproject/planemo/commit/a2c13e46259e3be35de1ecaae858ba818bb94734
.. _36f7cb11: https://github.com/galaxyproject/planemo/commit/36f7cb114f77731f90860d513a930e10ce5c1ba5
.. _b9232e55: https://github.com/galaxyproject/planemo/commit/b9232e55e713abbd1d9ce8b0b34cbec6c701dc17