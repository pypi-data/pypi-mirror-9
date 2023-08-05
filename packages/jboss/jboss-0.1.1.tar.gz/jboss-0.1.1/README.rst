JBoss API client
################

.. _description:

JBoss API client -- Short description.

.. _badges:

.. image:: http://img.shields.io/travis/klen/jboss.svg?style=flat-square
    :target: http://travis-ci.org/klen/jboss
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/klen/jboss.svg?style=flat-square
    :target: https://coveralls.io/r/klen/jboss
    :alt: Coverals

.. image:: http://img.shields.io/pypi/v/jboss.svg?style=flat-square
    :target: https://pypi.python.org/pypi/jboss

.. image:: http://img.shields.io/pypi/dm/jboss.svg?style=flat-square
    :target: https://pypi.python.org/pypi/jboss

.. image:: http://img.shields.io/gratipay/klen.svg?style=flat-square
    :target: https://www.gratipay.com/klen/
    :alt: Donate

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 2.6

.. _installation:

Installation
=============

**JBoss API client** should be installed using pip: ::

    pip install jboss

.. _usage:

Usage
=====

::
    from jboss import APIClient

    client = APIClient()
    response = client.api.runtime['test:dev:1.0'].process['process-name'].start.post()
    response = client.api.task.query(processInstanceId=response.json['id'])


.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/jboss/issues

.. _contributing:

Contributing
============

Development of JBoss API client happens at: https://github.com/klen/jboss


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
=======

Licensed under a `BSD license`_.

.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: https://github.com/klen
