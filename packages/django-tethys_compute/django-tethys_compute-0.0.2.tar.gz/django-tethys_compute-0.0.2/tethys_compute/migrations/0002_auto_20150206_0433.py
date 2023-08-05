# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import initialize_settings
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tethys_compute', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initialize_settings),
    ]
