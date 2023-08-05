
=============
Configuration
=============

This section contains information about how to configure your Django projects
to use *django-mysql-manager* and also contains a quick reference of the available
*settings* that can be used in order to customize the functionality of this
application.


MySQL Administrator Role
========================
This application requires that you create a MySQL user which will act as like
administrator for the user and database management.

A helper command exists for this purpose::

    $ ./manage.py generate_sql_statement_for_admin_user
    CREATE USER 'administrator'@'localhost' IDENTIFIED BY '1234';
    GRANT CREATE,DROP,REFERENCES,ALTER,DELETE,INDEX,INSERT,SELECT,UPDATE,CREATE \
    TEMPORARY TABLES,LOCK TABLES,CREATE VIEW,SHOW VIEW,ALTER ROUTINE,CREATE \
    ROUTINE,EXECUTE,CREATE USER,RELOAD ON *.* TO 'administrator'@'localhost' \
    WITH GRANT OPTION;

While in the MySQL shell as a superuser, create the *administrator* role::

    CREATE ROLE administrator WITH LOGIN CREATEDB CREATEROLE PASSWORD '1234';


Configuring your project
========================

Enter the database settings for the MySQL Manager::

    DATABASES = {
        ...
        # Database settings for mysql_manager
        'mysql_manager_conn': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mysql',      # Database name
            'USER': 'administrator',
            'PASSWORD': '1234',
            'HOST': '',
            'PORT': '',
        },
    }

In the Django project's ``settings`` module, add ``mysql_manager`` to the
``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'mysql_manager',
    )


Reference of the application settings
=====================================

The following settings can be specified in the Django project's ``settings``
module to customize the functionality of *django-mysql-manager*.

``SETTING_A``
    Setting A ...


Migrate the project database
============================

Finally, synchronize the project's database using the following command::

    python manage.py migrate

