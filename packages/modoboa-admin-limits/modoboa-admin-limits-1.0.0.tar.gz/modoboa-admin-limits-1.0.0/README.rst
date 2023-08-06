modoboa-admin-limits
====================

|travis| |landscape|

Per administrator limits for Modoboa.

Installation
------------

Install this extension system-wide or inside a virtual environment by
running the following command::

  $ pip install modoboa-admin-limits

Edit the settings.py file of your modoboa instance and add
``modoboa_admin_limits`` inside the ``MODOBOA_APPS`` variable like this::

    MODOBOA_APPS = (
      'modoboa',
      'modoboa.core',
      'modoboa.lib',
    
      # Extensions here
      'modoboa_admin',
      'modoboa_admin_limits',
    )

Run the following commands to setup the database tables::

  $ cd <modoboa_instance_dir>
  $ python manage.py migrate modoboa_admin_limits
  $ python manage.py load_initial_data
    
Finally, restart the python process running modoboa (uwsgi, gunicorn,
apache, whatever).

.. |landscape| image:: https://landscape.io/github/modoboa/modoboa-admin-limits/master/landscape.svg?style=flat
   :target: https://landscape.io/github/modoboa/modoboa-admin-limits/master
   :alt: Code Health
.. |travis| image:: https://travis-ci.org/modoboa/modoboa-admin-limits.png?branch=master
   :target: https://travis-ci.org/modoboa/modoboa-admin-limits
