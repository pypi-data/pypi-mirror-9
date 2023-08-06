# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Template name, for example, "headline"', max_length=255, verbose_name='Template name')),
                ('weight', models.IntegerField(default=0, verbose_name='Output order')),
                ('content', models.TextField(verbose_name='Content')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('only_for_superuser', models.BooleanField(default=False, verbose_name='Only for superuser')),
            ],
            options={
                'ordering': ['weight'],
                'verbose_name': 'Template',
                'verbose_name_plural': 'Template',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemplateGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Template group name')),
                ('description', models.TextField(verbose_name='Short description', blank=True)),
            ],
            options={
                'verbose_name': 'Template group',
                'verbose_name_plural': 'Template groups',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='template',
            name='group',
            field=models.ForeignKey(related_name=b'templates', verbose_name='Group', to='cmstemplates.TemplateGroup'),
            preserve_default=True,
        ),
    ]
