# Generated by Django 4.0.2 on 2022-02-11 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ScrapedItems', '0006_build'),
    ]

    operations = [
        migrations.AlterField(
            model_name='build',
            name='name',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='component',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.TextField(),
        ),
    ]
