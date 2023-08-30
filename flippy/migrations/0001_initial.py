# Generated by Django 4.2.4 on 2023-08-30 13:11

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlippyFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=150, unique=True)),
                ('boolean', models.BooleanField(null=True)),
                ('percentage_of_actors', models.IntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('percentage_of_time', models.IntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
        ),
        migrations.CreateModel(
            name='FlippyGroupGate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=150)),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enabled_groups', to='flippy.flippyfeature')),
            ],
        ),
        migrations.CreateModel(
            name='FlippyActorGate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=150)),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enabled_actors', to='flippy.flippyfeature')),
            ],
        ),
        migrations.AddConstraint(
            model_name='flippygroupgate',
            constraint=models.UniqueConstraint(fields=('key', 'feature'), name='group_feature_uniq'),
        ),
        migrations.AddConstraint(
            model_name='flippyactorgate',
            constraint=models.UniqueConstraint(fields=('key', 'feature'), name='actor_feature_uniq'),
        ),
    ]
