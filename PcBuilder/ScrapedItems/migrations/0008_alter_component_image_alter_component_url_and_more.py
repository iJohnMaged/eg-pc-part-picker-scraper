# Generated by Django 4.0.2 on 2022-02-11 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ScrapedItems', '0007_alter_build_name_alter_category_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='image',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='component',
            name='url',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='store',
            name='url',
            field=models.TextField(),
        ),
    ]
