# Generated by Django 3.2.20 on 2023-07-15 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tablebuilder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Table1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field1', models.CharField(max_length=255)),
                ('field2', models.IntegerField()),
            ],
            options={
                'app_label': 'tablebuilder',
            },
        ),
    ]
