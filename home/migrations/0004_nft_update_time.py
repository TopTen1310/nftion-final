# Generated by Django 4.1.3 on 2023-02-10 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_historyprice_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='nft',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
