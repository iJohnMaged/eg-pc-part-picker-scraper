# Generated by Django 4.0.2 on 2022-02-11 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ScrapedItems', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]