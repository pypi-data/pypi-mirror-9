# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jukedj.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, validators=[jukedj.validators.alphanum_vld])),
                ('description', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Atype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, validators=[jukedj.validators.alphanum_vld])),
                ('description', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, validators=[jukedj.validators.alphanum_vld])),
                ('description', models.TextField(default=b'', blank=True)),
                ('short', models.CharField(unique=True, max_length=10, validators=[jukedj.validators.alphanum_vld])),
                ('ordervalue', models.IntegerField(default=0)),
                ('assetflag', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_path', models.TextField(unique=True, verbose_name=b'the filepath to the file on some harddrive')),
                ('isopen', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('content', models.TextField(default=b'', blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, validators=[jukedj.validators.name_vld])),
                ('short', models.CharField(unique=True, max_length=10, validators=[jukedj.validators.alphanum_vld])),
                ('_path', models.TextField(unique=True, verbose_name=b'path to project root')),
                ('description', models.TextField(default=b'', blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('semester', models.CharField(max_length=50)),
                ('framerate', models.FloatField(default=25)),
                ('resx', models.IntegerField(default=1920, verbose_name=b'horizontal resolution')),
                ('resy', models.IntegerField(default=1020, verbose_name=b'vertical resolution')),
                ('scale', models.CharField(default=b'm', max_length=50, verbose_name=b'the maya scene scale')),
                ('status', models.CharField(default=b'New', max_length=50)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, validators=[jukedj.validators.alphanum_vld])),
                ('description', models.TextField(default=b'', blank=True)),
                ('project', models.ForeignKey(to='jukedj.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, validators=[jukedj.validators.alphanum_vld])),
                ('description', models.TextField(default=b'', blank=True)),
                ('startframe', models.IntegerField(default=1001)),
                ('endframe', models.IntegerField(default=1050)),
                ('handlesize', models.IntegerField(default=8)),
                ('assets', models.ManyToManyField(to='jukedj.Asset', null=True, blank=True)),
                ('project', models.ForeignKey(to='jukedj.Project')),
                ('sequence', models.ForeignKey(to='jukedj.Sequence')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, validators=[jukedj.validators.name_vld])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'New', max_length=50)),
                ('deadline', models.DateField(null=True, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('department', models.ForeignKey(to='jukedj.Department')),
                ('project', models.ForeignKey(to='jukedj.Project')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'ordering': ['department__ordervalue'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskFile',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jukedj.File')),
                ('version', models.IntegerField(default=1)),
                ('releasetype', models.CharField(max_length=20)),
                ('descriptor', models.TextField(null=True, blank=True)),
                ('typ', models.TextField(default=None)),
                ('task', models.ForeignKey(to='jukedj.Task')),
            ],
            options={
            },
            bases=('jukedj.file',),
        ),
        migrations.AlterUniqueTogether(
            name='taskfile',
            unique_together=set([('task', 'releasetype', 'version', 'descriptor', 'typ')]),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('department', 'content_type', 'object_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='shot',
            unique_together=set([('project', 'sequence', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='sequence',
            unique_together=set([('project', 'name')]),
        ),
        migrations.AddField(
            model_name='file',
            name='software',
            field=models.ForeignKey(blank=True, to='jukedj.Software', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='file',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='department',
            name='projects',
            field=models.ManyToManyField(to='jukedj.Project', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='atype',
            name='projects',
            field=models.ManyToManyField(to='jukedj.Project', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='atype',
            field=models.ForeignKey(verbose_name=b'asset type', to='jukedj.Atype'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='project',
            field=models.ForeignKey(to='jukedj.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='asset',
            unique_together=set([('project', 'atype', 'name')]),
        ),
    ]
