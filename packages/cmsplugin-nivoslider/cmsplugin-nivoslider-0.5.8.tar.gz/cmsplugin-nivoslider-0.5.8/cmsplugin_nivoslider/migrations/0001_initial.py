# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.folder


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        ('filer', '0002_auto_20150120_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='SliderPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=255, null=True, verbose_name='title', blank=True)),
                ('theme', models.CharField(default=b'default', max_length=50, verbose_name='theme', choices=[('dark', 'dark'), ('default', 'default'), ('bar', 'bar'), ('light', 'light')])),
                ('effect', models.CharField(default=b'random', max_length=50, verbose_name='effect', choices=[(b'sliceDown', b'sliceDown'), (b'sliceDownLeft', b'sliceDownLeft'), (b'sliceUp', b'sliceUp'), (b'sliceUpLeft', b'sliceUpLeft'), (b'sliceUpDown', b'sliceUpDown'), (b'sliceUpDownLeft', b'sliceUpDownLeft'), (b'fold', b'fold'), (b'fade', b'fade'), (b'random', b'random'), (b'slideInRight', b'slideInRight'), (b'slideInLeft', b'slideInLeft'), (b'boxRandom', b'boxRandom'), (b'boxRain', b'boxRain'), (b'boxRainReverse', b'boxRainReverse'), (b'boxRainGrow', b'boxRainGrow'), (b'boxRainGrowReverse', b'boxRainGrowReverse')])),
                ('manual_advance', models.BooleanField(default=False, verbose_name='manual advance')),
                ('anim_speed', models.PositiveIntegerField(default=500, help_text='Animation Speed (ms)', verbose_name='anim speed')),
                ('pause_time', models.PositiveIntegerField(default=3000, help_text='Pause time (ms)', verbose_name='pause time')),
                ('width', models.PositiveIntegerField(help_text='Width of the plugin (px)', null=True, verbose_name='width', blank=True)),
                ('height', models.PositiveIntegerField(help_text='Height of the plugin (px)', null=True, verbose_name='height', blank=True)),
                ('arrows', models.BooleanField(default=True, help_text='Arrow buttons for navigation', verbose_name='arrows')),
                ('thumbnails', models.BooleanField(default=False, help_text='Thumbnails for navigation [only works with the default theme!]', verbose_name='thumbnails')),
                ('random_start', models.BooleanField(default=False, verbose_name='random start')),
                ('pause_on_hover', models.BooleanField(default=True, verbose_name='pause on mouse hover')),
                ('album', filer.fields.folder.FilerFolderField(verbose_name='album', to='filer.Folder')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
