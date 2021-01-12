# Generated by Django 3.1.5 on 2021-01-11 01:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0021_auto_20210111_0139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='watch_listing',
        ),
        migrations.CreateModel(
            name='WatchList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('watch_listing', models.ManyToManyField(to='auctions.Listing')),
            ],
        ),
    ]