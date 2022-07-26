# Generated by Django 4.0.4 on 2022-06-30 12:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('softdesk', '0003_rename_users_assigned_contributor_user_assigned'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='relations_created', to=settings.AUTH_USER_MODEL),
        ),
    ]
