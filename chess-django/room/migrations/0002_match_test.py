# Generated by Django 5.0.3 on 2024-04-03 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='test',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
