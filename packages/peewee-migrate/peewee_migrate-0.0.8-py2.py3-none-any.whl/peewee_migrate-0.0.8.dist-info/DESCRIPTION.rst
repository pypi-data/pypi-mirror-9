Peewee Migrate
##############

.. _description:

Peewee Migrate -- A simple migration engine for Peewee

.. _badges:

.. image:: http://img.shields.io/travis/klen/peewee_migrate.svg?style=flat-square
    :target: http://travis-ci.org/klen/peewee_migrate
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/klen/peewee_migrate.svg?style=flat-square
    :target: https://coveralls.io/r/klen/pewee_migrate
    :alt: Coverals

.. image:: http://img.shields.io/pypi/v/peewee_migrate.svg?style=flat-square
    :target: https://pypi.python.org/pypi/peewee_migrate
    :alt: Version

.. image:: http://img.shields.io/pypi/dm/peewee_migrate.svg?style=flat-square
    :target: https://pypi.python.org/pypi/peewee_migrate
    :alt: Downloads

.. image:: http://img.shields.io/gratipay/klen.svg?style=flat-square
    :target: https://www.gratipay.com/klen/
    :alt: Donate

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python 2.7,3.3,3.4

.. _installation:

Installation
=============

**Peewee Migrate** should be installed using pip: ::

    pip install peewee_migrate

.. _usage:

Usage
=====

>From shell
----------

Getting help: ::

    $ pw_migrate --help

    Usage: pw_migrate [OPTIONS] COMMAND [ARGS]...

    Options:
        --help  Show this message and exit.

    Commands:
        create   Create migration.
        migrate  Run migrations.

Create migration: ::

    $ pw_migrate create --help

    Usage: pw_migrate create [OPTIONS] NAME

        Create migration.

    Options:
        --database TEXT   Database connection
        --directory TEXT  Directory where migrations are stored
        -v, --verbose
        --help            Show this message and exit.

Run migrations: ::

    $ pw_migrate migrate --help

    Usage: pw_migrate migrate [OPTIONS]

        Run migrations.

    Options:
        --name TEXT       Select migration
        --database TEXT   Database connection
        --directory TEXT  Directory where migrations are stored
        -v, --verbose
        --help            Show this message and exit.

>From python
-----------
::

    from peewee_migrate.core import Router

    router = Router('migrations', DATABASE='sqlite:///test.db')

    # Create migration
    router.create('migration_name')

    # Run migration/migrations
    router.run('migration_name')

    # Run all unapplied migrations
    router.run()


.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/peewee_migrate/issues

.. _contributing:

Contributing
============

Development of starter happens at github: https://github.com/klen/peewee_migrate


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
=======

Licensed under a `BSD license`_.

.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.com/


