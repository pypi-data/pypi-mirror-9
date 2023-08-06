
=======================
Data management in bulk
=======================

This section contains information, including examples, about how to manage data
in bulk directly through the web interface or by using the command line interface.


Using the Web Administration Interface
======================================

TODO

Using actions:

- set zone type (NATIVE, MASTER, SLAVE)
- set TTL on all resource records of the selected zone.


Using the Command Line Interface
================================

*django-powerdns-manager* implements the following commands:

- ``exportzones``
- ``importzones``
- ``importaxfr``

To get help about the syntax of each command run::

    python manage.py [command] --help


exportzones
-----------

To export all zones or some zones to the current directory::

    python manage.py exportzones --all
    python manage.py exportzones example.org example.net
    
To export all zones or some zones to the specified directory::

    python manage.py exportzones -d /var/lib/dns/tmp --all
    python manage.py exportzones -d /var/lib/dns/tmp example.org example.net


importzones
-----------

To import zones from zonefiles::

    python manage.py importzones example.org.zonefile example.net.zonefile

To import zones overwriting existing ones::

    python manage.py importzones --overwrite example.org.zonefile example.net.zonefile


importaxfr
----------

To import ``example.org`` ``example.net`` from nameserver ``192.168.0.254``
using an AXFR query::

    python manage.py importaxfr --nameserver 192.168.0.254 example.org example.net
    
To import all zones listed in a text file (one zone per line) from nameserver
``192.168.0.254`` using an AXFR query::

    python manage.py importaxfr --nameserver 192.168.0.254 --domainfile myzones.txt

To also overwrite existing zones, use the ``--overwrite`` switch::

    python manage.py importaxfr -n 192.168.0.254 -d myzones.txt -o

