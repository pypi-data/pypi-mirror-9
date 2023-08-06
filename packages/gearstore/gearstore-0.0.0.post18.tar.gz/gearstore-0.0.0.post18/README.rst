===============================
gearstore
===============================

A Gearman worker to do distributed job persistence for reliable delivery

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/gearstore
* Source: http://git.openstack.org/cgit/openstack-infra/gearstore
* Bugs: http://bugs.launchpad.net/gearstore

Inspiration
-----------

This project is inspired by dormando's Garivini. Since that one is in
Perl, and we don't like supporting perl, we are reimplementing the same
interface in python with the gear library.

See https://github.com/dormando/Garivini for more.

Features
--------

* Distributed message persistence for Gearman jobs makes persistence scale out.
* No centralized store makes system more fault tolerant.

Quick Start
-----------

Gearstore is pip installable. Once it has been installed, you will need
to initialize the database schema::

  gearstore-init-schema mysql://user:pass@host/dbname

You will also need a gearman server available. The library used by
gearstore, gear, includes one and it will be availalbe in the same
place as gearstore as  `geard`::

  geard

Once the database is initialized, run as many gearstores as is needed
to keep traffic flowing::

  gearstore --sqlalchemy-dsn=mysql://user:pass@host/dbname 
