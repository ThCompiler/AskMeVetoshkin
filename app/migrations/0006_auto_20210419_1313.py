# Generated by Django 3.1.7 on 2021-04-19 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_answer_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['date'], 'verbose_name': 'Ответ', 'verbose_name_plural': 'Ответы'},
        ),
    ]
