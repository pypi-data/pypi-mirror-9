# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waffle', '0003_verifieduser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flag',
            name='sessions',
        ),
    ]
