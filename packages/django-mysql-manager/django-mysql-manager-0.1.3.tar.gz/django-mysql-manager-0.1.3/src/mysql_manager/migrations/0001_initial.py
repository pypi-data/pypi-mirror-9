# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MySQLDatabase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(help_text=b'Enter a name for the PostgreSQL database.', unique=True, max_length=100, verbose_name=b'name')),
                ('charset_name', models.CharField(default=b'utf8', help_text=b'Enter the character set for this database.', max_length=30, verbose_name=b'character set')),
                ('collation_name', models.CharField(default=b'utf8_unicode_ci', help_text=b'Enter the collation for this database.', max_length=30, verbose_name=b'collation')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name=b'created on')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name=b'last modified on')),
                ('created_by', models.ForeignKey(related_name='mysql_manager_mysqldatabase_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'MySQL Database',
                'verbose_name_plural': 'MySQL Databases',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySQLUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(help_text=b'Enter a name for the MySQL user', unique=True, max_length=55, verbose_name='name')),
                ('is_active', models.BooleanField(default=True, help_text=b'Mark the user as active or not. A user that is marked as inactive cannot login to the PostgreSQL cluster.', db_index=True, verbose_name=b'active')),
                ('max_queries_per_hour', models.PositiveIntegerField(default=0, help_text=b'Restrict the number of queries permitted to this account during any given one-hour period. If this is set to 0 (the default), this means that there is no limitation for the account.', verbose_name=b'max queries per hour')),
                ('max_updates_per_hour', models.PositiveIntegerField(default=0, help_text=b'Restrict the number of updates permitted to this account during any given one-hour period. If this is set to 0 (the default), this means that there is no limitation for the account.', verbose_name=b'max updates per hour')),
                ('max_connections_per_hour', models.PositiveIntegerField(default=0, help_text=b'Restrict the number of connections permitted to this account during any given one-hour period. If this is set to 0 (the default), this means that there is no limitation for the account.', verbose_name=b'max connections per hour')),
                ('max_user_connections', models.PositiveIntegerField(default=0, help_text=b'Restricts the maximum number of simultaneous connections to the server by the account. A nonzero value specifies the limit for the account explicitly. If value is 0 (the default), the server determines the number of simultaneous connections for the account from the global value of the ``max_user_connections`` system variable. If ``max_user_connections`` is also zero, there is no limit for the account.', verbose_name=b'max user connections')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name=b'created on')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name=b'last modified on')),
                ('created_by', models.ForeignKey(related_name='mysql_manager_mysqluser_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'MySQL User',
                'verbose_name_plural': 'MySQL Users',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mysqldatabase',
            name='user',
            field=models.ForeignKey(related_name='mysql_manager_mysqldatabase_user', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='mysql_manager.MySQLUser', help_text=b'Select the user that owns the database.', null=True, verbose_name='user'),
            preserve_default=True,
        ),
    ]
