# Generated by Django 4.1.2 on 2022-10-19 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_message_station'),
    ]

    operations = [
        migrations.RenameField(
            model_name='station',
            old_name='name',
            new_name='name_long',
        ),
        migrations.RemoveField(
            model_name='station',
            name='elevator',
        ),
        migrations.RemoveField(
            model_name='station',
            name='id',
        ),
        migrations.RemoveField(
            model_name='station',
            name='ov_bike',
        ),
        migrations.RemoveField(
            model_name='station',
            name='park_and_ride',
        ),
        migrations.RemoveField(
            model_name='station',
            name='toilet',
        ),
        migrations.AddField(
            model_name='station',
            name='name_mid',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='station',
            name='name_short',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='station',
            name='uiccode',
            field=models.CharField(default='', max_length=7, primary_key=True, serialize=False, unique=True),
            preserve_default=False,
        ),
    ]