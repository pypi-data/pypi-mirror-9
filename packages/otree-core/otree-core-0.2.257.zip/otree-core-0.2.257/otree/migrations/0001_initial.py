# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import save_the_change.mixins
import otree.models.session
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedGroupWaitPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page_index', otree.db.models.PositiveIntegerField(null=True)),
                ('session_pk', otree.db.models.PositiveIntegerField(null=True)),
                ('group_pk', otree.db.models.PositiveIntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompletedSubsessionWaitPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page_index', otree.db.models.PositiveIntegerField(null=True)),
                ('session_pk', otree.db.models.PositiveIntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Experimenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_index_in_game_pages', otree.db.models.PositiveIntegerField(default=0, null=True)),
                ('round_number', otree.db.models.PositiveIntegerField(null=True)),
                ('subsession_object_id', otree.db.models.PositiveIntegerField(null=True)),
            ],
            options={
            },
            bases=(save_the_change.mixins.SaveTheChange, models.Model),
        ),
        migrations.CreateModel(
            name='GlobalSingleton',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('admin_access_code', otree.db.models.RandomCharField(max_length=8, blank=True)),
            ],
            options={
                'verbose_name': 'Set open session',
                'verbose_name_plural': 'Set open session',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageCompletion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_name', otree.db.models.CharField(max_length=300, null=True)),
                ('player_pk', otree.db.models.PositiveIntegerField(null=True)),
                ('page_index', otree.db.models.PositiveIntegerField(null=True)),
                ('page_name', otree.db.models.CharField(max_length=300, null=True)),
                ('time_stamp', otree.db.models.PositiveIntegerField(null=True)),
                ('seconds_on_page', otree.db.models.PositiveIntegerField(null=True)),
                ('subsession_pk', otree.db.models.PositiveIntegerField(null=True)),
                ('participant_pk', otree.db.models.PositiveIntegerField(null=True)),
                ('session_pk', otree.db.models.PositiveIntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vars', otree.db.models.PickleField(default=otree.models.session.model_vars_default, null=True)),
                ('_index_in_subsessions', otree.db.models.PositiveIntegerField(default=0, null=True)),
                ('_index_in_pages', otree.db.models.PositiveIntegerField(default=0, null=True)),
                ('id_in_session', otree.db.models.PositiveIntegerField(null=True)),
                ('_waiting_for_ids', otree.db.models.CharField(max_length=300, null=True)),
                ('code', otree.db.models.RandomCharField(max_length=8, blank=True)),
                ('last_request_succeeded', otree.db.models.NullBooleanField(verbose_name=b'Health of last server request', choices=[(True, 'Yes'), (False, 'No')])),
                ('visited', otree.db.models.BooleanField(default=False)),
                ('ip_address', otree.db.models.GenericIPAddressField(null=True)),
                ('_last_page_timestamp', otree.db.models.PositiveIntegerField(null=True)),
                ('_last_request_timestamp', otree.db.models.PositiveIntegerField(null=True)),
                ('is_on_wait_page', otree.db.models.BooleanField(default=False)),
                ('_current_page_name', otree.db.models.CharField(max_length=200, null=True, verbose_name=b'page')),
                ('_current_app_name', otree.db.models.CharField(max_length=200, null=True, verbose_name=b'app')),
                ('_round_number', otree.db.models.PositiveIntegerField(null=True)),
                ('_current_form_page_url', otree.db.models.URLField(null=True)),
                ('_max_page_index', otree.db.models.PositiveIntegerField(null=True)),
                ('exclude_from_data_analysis', otree.db.models.BooleanField(default=False)),
                ('time_started', otree.db.models.DateTimeField(null=True)),
                ('mturk_assignment_id', otree.db.models.CharField(max_length=50, null=True)),
                ('mturk_worker_id', otree.db.models.CharField(max_length=50, null=True)),
                ('label', otree.db.models.CharField(max_length=50, null=True)),
                ('_predetermined_arrival_order', otree.db.models.PositiveIntegerField(null=True)),
            ],
            options={
                'ordering': ['pk'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vars', otree.db.models.PickleField(default=otree.models.session.model_vars_default, null=True)),
                ('session_type_name', otree.db.models.CharField(max_length=300, null=True, blank=True)),
                ('label', otree.db.models.CharField(help_text=b'For internal record-keeping', max_length=300, null=True, blank=True)),
                ('experimenter_name', otree.db.models.CharField(help_text=b'For internal record-keeping', max_length=300, null=True, blank=True)),
                ('code', otree.db.models.RandomCharField(max_length=8, blank=True)),
                ('money_per_point', otree.db.models.DecimalField(null=True, max_digits=12, decimal_places=5)),
                ('time_scheduled', otree.db.models.DateTimeField(help_text=b'For internal record-keeping', null=True)),
                ('time_started', otree.db.models.DateTimeField(null=True)),
                ('mturk_payment_was_sent', otree.db.models.BooleanField(default=False)),
                ('hidden', otree.db.models.BooleanField(default=False)),
                ('git_commit_timestamp', otree.db.models.CharField(max_length=200, null=True)),
                ('fixed_pay', otree.db.models.CurrencyField(null=True, max_digits=12)),
                ('comment', otree.db.models.TextField(null=True)),
                ('_players_assigned_to_groups', otree.db.models.BooleanField(default=False)),
                ('special_category', otree.db.models.CharField(max_length=20, null=True)),
                ('demo_already_used', otree.db.models.BooleanField(default=False)),
                ('ready', otree.db.models.BooleanField(default=False)),
                ('_pre_create_id', otree.db.models.CharField(max_length=300, null=True)),
            ],
            options={
                'ordering': ['pk'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SessionExperimenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vars', otree.db.models.PickleField(default=otree.models.session.model_vars_default, null=True)),
                ('_index_in_subsessions', otree.db.models.PositiveIntegerField(default=0, null=True)),
                ('_index_in_pages', otree.db.models.PositiveIntegerField(default=0, null=True)),
                ('id_in_session', otree.db.models.PositiveIntegerField(null=True)),
                ('_waiting_for_ids', otree.db.models.CharField(max_length=300, null=True)),
                ('code', otree.db.models.RandomCharField(max_length=8, blank=True)),
                ('last_request_succeeded', otree.db.models.NullBooleanField(verbose_name=b'Health of last server request', choices=[(True, 'Yes'), (False, 'No')])),
                ('visited', otree.db.models.BooleanField(default=False)),
                ('ip_address', otree.db.models.GenericIPAddressField(null=True)),
                ('_last_page_timestamp', otree.db.models.PositiveIntegerField(null=True)),
                ('_last_request_timestamp', otree.db.models.PositiveIntegerField(null=True)),
                ('is_on_wait_page', otree.db.models.BooleanField(default=False)),
                ('_current_page_name', otree.db.models.CharField(max_length=200, null=True, verbose_name=b'page')),
                ('_current_app_name', otree.db.models.CharField(max_length=200, null=True, verbose_name=b'app')),
                ('_round_number', otree.db.models.PositiveIntegerField(null=True)),
                ('_current_form_page_url', otree.db.models.URLField(null=True)),
                ('_max_page_index', otree.db.models.PositiveIntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SessionuserToUserLookup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_user_pk', otree.db.models.PositiveIntegerField(null=True)),
                ('page_index', otree.db.models.PositiveIntegerField(null=True)),
                ('app_name', otree.db.models.CharField(max_length=300, null=True)),
                ('user_pk', otree.db.models.PositiveIntegerField(null=True)),
                ('is_experimenter', otree.db.models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StubModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WaitPageVisit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_pk', otree.db.models.PositiveIntegerField(null=True)),
                ('page_index', otree.db.models.PositiveIntegerField(null=True)),
                ('id_in_session', otree.db.models.PositiveIntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='session',
            name='session_experimenter',
            field=otree.db.models.OneToOneField(related_name='session', null=True, to='otree.SessionExperimenter'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participant',
            name='session',
            field=otree.db.models.ForeignKey(to='otree.Session'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='globalsingleton',
            name='open_session',
            field=otree.db.models.ForeignKey(blank=True, to='otree.Session', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimenter',
            name='session',
            field=otree.db.models.ForeignKey(related_name='otree_experimenter', to='otree.Session'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimenter',
            name='session_experimenter',
            field=otree.db.models.ForeignKey(related_name='experimenter', to='otree.SessionExperimenter', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimenter',
            name='subsession_content_type',
            field=otree.db.models.ForeignKey(related_name='experimenter', to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ParticipantProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Monitor Participant',
                'proxy': True,
                'verbose_name_plural': 'Monitor Participants',
            },
            bases=('otree.participant',),
        ),
    ]
