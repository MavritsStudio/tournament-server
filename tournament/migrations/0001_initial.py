# Generated by Django 4.2.6 on 2023-10-22 06:35

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import tournament.validators
import utils.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('match', '0001_initial'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('code', models.CharField(default=utils.utils.get_uuid_hex, max_length=32, primary_key=True, serialize=False, verbose_name='code')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='name')),
                ('description', models.TextField(max_length=512, verbose_name='description')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'opened'), (1, 'active'), (2, 'finished'), (3, 'cancelled')], default=0, verbose_name='status')),
                ('contact', models.CharField(blank=True, default='', help_text='Free format contact, can be link, phone number, etc.', max_length=50, verbose_name='organizer contact')),
                ('limit', models.PositiveSmallIntegerField(default=16, validators=[django.core.validators.MinValueValidator(4), django.core.validators.MaxValueValidator(16)], verbose_name='teams count limit')),
                ('start', models.DateTimeField(default=None, null=True, verbose_name='start date')),
                ('finish', models.DateTimeField(default=None, null=True, verbose_name='finish date')),
                ('organizer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='organizer')),
                ('teams', models.ManyToManyField(related_name='tournaments', to='account.team', verbose_name='participant teams')),
            ],
            options={
                'verbose_name': 'tournament',
                'verbose_name_plural': 'tournaments',
                'ordering': ['status', '-finish', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='number')),
                ('match', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='match.match', verbose_name='match')),
                ('next_match', models.ForeignKey(help_text='Helps to keep tournament bracket hierarchy information. None value means this match is final.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='childs', to='match.match', verbose_name='related match')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.tournament', verbose_name='tournament')),
            ],
            options={
                'verbose_name': 'tournament round',
                'verbose_name_plural': 'tournament rounds',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=10, validators=[tournament.validators.place_value_validator], verbose_name='place')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='account.team', verbose_name='team')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to='tournament.tournament', verbose_name='tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='places', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'place',
                'verbose_name_plural': 'places',
            },
        ),
        migrations.AddConstraint(
            model_name='round',
            constraint=models.UniqueConstraint(condition=models.Q(('next_match__isnull', True)), fields=('tournament',), name='tournament_has_only_one_final_match'),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together={('user', 'team', 'tournament'), ('user', 'tournament')},
        ),
    ]
