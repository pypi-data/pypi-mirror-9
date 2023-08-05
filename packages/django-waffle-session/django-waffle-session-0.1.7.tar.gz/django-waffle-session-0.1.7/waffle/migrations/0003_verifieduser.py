# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waffle', '0002_flag_sessions'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerifiedUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=255)),
                ('feature', models.ForeignKey(to='waffle.Flag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
