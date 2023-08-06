# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import oauth_api.generators
import oauth_api.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'updated')),
                ('token', models.CharField(max_length=255, db_index=True)),
                ('expires', models.DateTimeField()),
                ('scope', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'updated')),
                ('client_id', models.CharField(default=oauth_api.generators.generate_client_id, unique=True, max_length=100)),
                ('redirect_uris', models.TextField(help_text='Allowed URIs list, line separated', blank=True, validators=[oauth_api.utils.validate_uris])),
                ('client_type', models.CharField(max_length=32, choices=[(b'confidential', 'Confidential'), (b'public', 'Public')])),
                ('authorization_grant_type', models.CharField(max_length=32, choices=[(b'authorization-code', 'Authorization code'), (b'implicit', 'Implicit'), (b'password', 'Resource owner password-based'), (b'client-credentials', 'Client credentials')])),
                ('client_secret', models.CharField(default=oauth_api.generators.generate_client_secret, max_length=255, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthorizationCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'updated')),
                ('code', models.CharField(max_length=255)),
                ('expires', models.DateTimeField()),
                ('redirect_uri', models.CharField(max_length=255)),
                ('scope', models.TextField(blank=True)),
                ('application', models.ForeignKey(to='oauth_api.Application')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RefreshToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'updated')),
                ('token', models.CharField(max_length=255)),
                ('expires', models.DateTimeField(null=True, blank=True)),
                ('access_token', models.OneToOneField(related_name='refresh_token', to='oauth_api.AccessToken')),
                ('application', models.ForeignKey(to='oauth_api.Application')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='application',
            field=models.ForeignKey(to='oauth_api.Application'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
