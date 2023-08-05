=============================
versioneer2
=============================

.. image:: https://travis-ci.org/ryanpdwyer/versioneer2.png?branch=master
    :target: https://travis-ci.org/ryanpdwyer/versioneer2


An updated, simplified version of versioneer.

Development Note
----------------

Since this project uses itself for versioning, when you make a change to the main stript
 (versioneer2/__init__.py), you should then run the following commands::

    python setup.py install
    versioneer2installer
    python setup.py versioneer


Then your changes have actually updated both __init__.py and the bundled copy of versioneer. To see the effect of all of your changes, run setup.py install again and test normally.





History
-------

0.1.0 (2015-01-16)
++++++++++++++++++

* First release on PyPI.


