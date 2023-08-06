modoboa-stats
=============

|landscape|

Graphical statistics for Modoboa.

Installation
------------

Install this extension system-wide or inside a virtual environment by
running the following command::

  $ pip install modoboa-stats

Edit the settings.py file of your modoboa instance and add
``modoboa_stats`` inside the ``MODOBOA_APPS`` variable like this::

    MODOBOA_APPS = (
      'modoboa',
      'modoboa.core',
      'modoboa.lib',
    
      # Extensions here
      # ...
      'modoboa_admin',
      'modoboa_stats',
    )

Run the following commands to setup the database tables::

  $ cd <modoboa_instance_dir>
  $ python manage.py load_initial_data
    
Finally, restart the python process running modoboa (uwsgi, gunicorn,
apache, whatever).

.. |landscape| image:: https://landscape.io/github/modoboa/modoboa-stats/master/landscape.svg?style=flat
   :target: https://landscape.io/github/modoboa/modoboa-stats/master
   :alt: Code Health

