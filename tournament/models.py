from itertools import chain
from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from account.models import Team
from match.models import Match
from utils.utils import get_uuid_hex

from tournament.validators import place_value_validator


class Tournament(models.Model):
    class StatusChoice(models.IntegerChoices):
        OPENED = 0, _('opened')
        ACTIVE = 1, _('active')
        FINISHED = 2, _('finished')
        CANCELLED = 3, _('cancelled')

    code = models.CharField(
        _('code'), max_length=32,
        primary_key=True, default=get_uuid_hex,
    )

    name = models.CharField(_('name'), max_length=64, unique=True)
    description = models.TextField(_('description'), max_length=512)
    status = models.PositiveSmallIntegerField(
        _('status'), choices=StatusChoice.choices, default=StatusChoice.OPENED,
    )
    organizer = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL,
        verbose_name=_('organizer'), null=True,
    )
    contact = models.CharField(
        _('organizer contact'), max_length=50,
        help_text=_('Free format contact, can be link, phone number, etc.'),
        blank=True, default='',
    )

    limit = models.PositiveSmallIntegerField(
        _('teams count limit'), default=16,
        validators=[MinValueValidator(4), MaxValueValidator(16),],
    )

    teams = models.ManyToManyField(
        Team, verbose_name=_('participant teams'), related_name='tournaments',
    )

    start = models.DateTimeField(_('start date'), null=True, default=None)
    finish = models.DateTimeField(_('finish date'), null=True, default=None)

    class Meta:
        verbose_name = _('tournament')
        verbose_name_plural = _('tournaments')
        ordering = ['status', '-finish', 'name']

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def get_next_power_of_2(
        value: int, step: int = 0, _container: int = 1,
    ) -> int:
        if value < 1:
            raise ValueError(
                'Can not to find next power of 2 for negative and zero.',
            )

        if value <= _container:
            return step

        return Tournament.get_next_power_of_2(
            value, step + 1, _container * 2,
        )

    @property
    def teams_count(self) -> int:
        return self.teams.all().count()

    @property
    def participant_user_ids(self) -> list[str]:
        return list(chain(
            *[[team.mate1_id, team.mate2_id] for team in self.teams.all()]
        ))

    def append_team(self, team: Team) -> None:
        if self.status != self.StatusChoice.OPENED:
            raise ValidationError(
                _('Can not to append new team to the closed tournament.'),
            )

        teams = list[self.teams.all()]

        if self.limit - len(teams) < 1:
            raise ValidationError(
                _('Tournament teams limit is over.')
            )

        if team in teams:
            raise ValidationError(
                _('Team already register at this tournament.'),
            )

        users = list(chain(*[[_team.mate1, _team.mate2] for _team in teams]))
        repeated_user = (
            (team.mate1 if team.mate1_id in users else None)
            or (team.mate2 if team.mate2 in users else None)
        )

        if repeated_user:
            raise ValidationError(
                _('The %(user)s is already the tournament participant.'),
                params={'user': repeated_user}
            )

        self.teams.add(team)

    def activate(self):
        if self.status != self.StatusChoice.OPENED:
            raise ValidationError(
                _('Can to activate only opened tournaments.'),
            )

        if self.teams.all().count() < 4:
            raise ValidationError(
                _('Can not to start tournament with less then 4 teams.'),
            )

        self.status = self.StatusChoice.ACTIVE
        self.start = datetime.now()
        self.save()

        from tournament.tasks import initialize_bracket

        initialize_bracket(self)

    def get_place_by_round_lose(self, round_number: int) -> str:
        teams = self.teams_count
        border = self.get_next_power_of_2(teams)

        if round_number == 1:
            return f'{2 ** (border - 1) + 1}-{teams}'

        if border - round_number - 1 < 1:
            raise ValueError(_('Unexpected round number'))

        upper = 2 ** (border - round_number - 1)

        return '%d-%d' % (upper // 2 + 1, upper)


class Round(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE,
        verbose_name=_('tournament'),
    )

    number = models.PositiveSmallIntegerField(
        _('number'), validators=[MinValueValidator(1)],
    )

    match = models.OneToOneField(
        Match, on_delete=models.PROTECT,
        verbose_name=_('match'),
    )

    next_match = models.ForeignKey(
        Match, on_delete=models.SET_NULL,
        verbose_name=_('related match'), related_name='childs',
        null=True,
        help_text=_(
            'Helps to keep tournament bracket hierarchy information. '
            'None value means this match is final.',
        ),
    )

    class Meta:
        verbose_name = _('tournament round')
        verbose_name_plural = _('tournament rounds')
        constraints = [
            models.UniqueConstraint(
                fields=['tournament'],
                condition=models.Q(next_match__isnull=True),
                name='tournament_has_only_one_final_match',
            )
        ]


class Place(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE,
        verbose_name=_('tournament'), related_name='places',
    )

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        verbose_name=_('user'), related_name='places',
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        verbose_name=_('team'), related_name='places',
    )

    place = models.CharField(
        _('place'), max_length=10, validators=[place_value_validator,],
    )

    created = models.DateTimeField(_('date created'), auto_now_add=True)

    class Meta:
        verbose_name = _('place')
        verbose_name_plural = _('places')
        unique_together = [
            ['user', 'team', 'tournament'],
            ['user', 'tournament'],
        ]
