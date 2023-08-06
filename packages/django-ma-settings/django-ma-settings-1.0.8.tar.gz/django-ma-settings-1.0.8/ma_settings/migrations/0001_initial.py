# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MasterSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('display_name', models.CharField(max_length=255, verbose_name='Display name')),
                ('value', models.CharField(max_length=1000, null=True, verbose_name='Setting value')),
                ('type', models.CharField(max_length=10, verbose_name='Setting type', choices=[(b'integer', b'Integer'), (b'string', b'String'), (b'choices', b'Choices'), (b'float', b'Float'), (b'foreign', b'Foreign key')])),
                ('foreign_model', models.CharField(max_length=255, null=True, verbose_name='Foreign model')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
