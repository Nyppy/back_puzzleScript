# Generated by Django 3.2.6 on 2021-08-19 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_filemanager_short_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemanager',
            name='text_doc',
            field=models.FileField(null=True, upload_to='media/doc'),
        ),
        migrations.AlterField(
            model_name='filemanager',
            name='video',
            field=models.FileField(upload_to='media'),
        ),
    ]
