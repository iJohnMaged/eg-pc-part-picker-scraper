# Generated by Django 4.0.2 on 2022-02-11 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ScrapedItems', '0002_alter_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='recently_scraped',
            field=models.BooleanField(default=True),
        ),
    ]
