# Generated by Django 3.1.3 on 2020-11-13 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_urlmapping_opened'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharefile',
            name='doctor_name',
            field=models.CharField(default='', max_length=250),
        ),
    ]
