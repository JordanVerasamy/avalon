# Generated by Django 2.0 on 2017-12-21 06:21

import app.models
from django.db import migrations
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_player_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='role',
            field=enumfields.fields.EnumField(enum=app.models.Role, max_length=12, null=True),
        ),
    ]