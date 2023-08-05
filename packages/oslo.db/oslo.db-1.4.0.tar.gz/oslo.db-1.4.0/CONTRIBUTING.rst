=================
How to contribute
=================

If you would like to contribute to the development of OpenStack,
you must follow the steps in this page:

   http://docs.openstack.org/infra/manual/developers.html

Once those steps have been completed, changes to OpenStack
should be submitted for review via the Gerrit tool, following
the workflow documented at:

   http://docs.openstack.org/infra/manual/developers.html#development-workflow

Pull requests submitted through GitHub will be ignored.

Bugs should be filed on Launchpad, not GitHub:

   https://bugs.launchpad.net/oslo.db


How to run unit tests
=====================

oslo.db (as all OpenStack projects) uses tox to run unit tests. You can find
general information about OpenStack unit tests and testing with tox in wiki_.

oslo.db tests use MySQL-python as the default MySQL DB API driver (which is
true for OpenStack), and psycopg2 for PostgreSQL. pip will build these libs in
your venv, so you must ensure that you have the required system packages
installed.  For Ubuntu/Debian they are python-dev, libmysqlclient-dev and
libpq-dev.  For Fedora/CentOS - gcc, python-devel, postgresql-devel and
mysql-devel.

The oslo.db unit tests system allows to run unittests on real databases. At the
moment it supports MySQL, PostgreSQL and SQLite.
For testing on a real database backend you need to set up a user
``openstack_citest`` with password ``openstack_citest`` on localhost (some
OpenStack projects require a database named 'openstack_citest' too).
Please note, that this user must have permissions to create and drop databases.
If the testing system is not able to connect to the backend, tests on it will
be skipped.

For PostgreSQL on Ubuntu you can create a user in the following way::

 sudo -u postgres psql
 postgres=# create user openstack_citest with createdb login password
            'openstack_citest';

For MySQL you can use the following commands::

 mysql -u root
 mysql> CREATE USER 'openstack_citest'@'localhost' IDENTIFIED BY
        'openstack_citest';
 mysql> GRANT ALL PRIVILEGES ON * . * TO 'openstack_citest'@'localhost';
 mysql> FLUSH PRIVILEGES;

.. _wiki: https://wiki.openstack.org/wiki/Testing#Unit_Tests
