modoboa-admin-relaydomains
==========================

|travis| |landscape|

Relay domains support for Modoboa.

Installation
------------

Install this extension system-wide or inside a virtual environment by
running the following command::

  $ pip install modoboa-admin-relaydomains

Edit the settings.py file of your modoboa instance and add
``modoboa_admin_relaydomains`` inside the ``MODOBOA_APPS`` variable like this::

    MODOBOA_APPS = (
      'modoboa',
      'modoboa.core',
      'modoboa.lib',
    
      # Extensions here
      'modoboa_admin',
      'modoboa_admin_relaydomains',
    )

Run the following commands to setup the database tables::

  $ cd <modoboa_instance_dir>
  $ python manage.py migrate modoboa_admin_relaydomains
  $ python manage.py load_initial_data
    
Finally, restart the python process running modoboa (uwsgi, gunicorn,
apache, whatever).

.. |landscape| image:: https://landscape.io/github/modoboa/modoboa-admin-relaydomains/master/landscape.svg?style=flat
   :target: https://landscape.io/github/modoboa/modoboa-admin-relaydomains/master
   :alt: Code Health
.. |travis| image:: https://travis-ci.org/modoboa/modoboa-admin-relaydomains.png?branch=master
   :target: https://travis-ci.org/modoboa/modoboa-admin-relaydomains
