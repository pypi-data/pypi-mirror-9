# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jukedj', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='assets',
            field=models.ManyToManyField(to='jukedj.Asset'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='resy',
            field=models.IntegerField(default=1080, verbose_name=b'vertical resolution'),
        ),
    ]
