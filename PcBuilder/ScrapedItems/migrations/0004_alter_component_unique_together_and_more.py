# Generated by Django 4.0.2 on 2022-02-11 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ScrapedItems', '0003_component_recently_scraped'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='component',
            unique_together={('name', 'store', 'category')},
        ),
        migrations.AlterUniqueTogether(
            name='store',
            unique_together={('name', 'url')},
        ),
    ]
