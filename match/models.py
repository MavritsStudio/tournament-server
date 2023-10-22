from typing import Optional
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from account.models import Team
from utils.utils import get_uuid_hex


class Match(models.Model):
    class StatusChoice(models.IntegerChoices):
        SCHEDULED = 0, _('scheduled')
        ONGOING = 1, _('ongoing')
        FINISHED = 2, _('finished')
        WALK_OVER = 3, _('walk-over')

    code = models.CharField(
        _('code'), max_length=32,
        primary_key=True, default=get_uuid_hex,
    )
    status = models.PositiveSmallIntegerField(
        _('status'),
        choices=StatusChoice.choices, default=StatusChoice.SCHEDULED,
    )

    participant1 = models.ForeignKey(
        Team, on_delete=models.PROTECT,
        verbose_name=_('team as participant-1'),
        related_name='participated1',
        null=True, default=None,
    )
    participant2 = models.ForeignKey(
        Team, on_delete=models.PROTECT,
        verbose_name=_('team as participant-2'),
        related_name='participated2',
        null=True, default=None,
    )

    score1 = models.PositiveSmallIntegerField(
        _('participant1 match score'), null=True, default=None,
        help_text=_(
            'The None value means that match hast not been finished.',
        ),
    )
    score2 = models.PositiveSmallIntegerField(
        _('participant2 match score'), null=True, default=None,
        help_text=_(
            'The None value means that match hast not been finished.',
        ),
    )

    finish = models.DateTimeField(_('finish date'), null=True, default=None)

    class Meta:
        verbose_name = _('match')
        verbose_name_plural = _('matches')
        ordering = ['status', '-finish']

    def __str__(self) -> str:
        return self.code
    
    def clean(self) -> None:
        if (
            self.participant1
            and self.participant2
            and self.participant1 == self.participant2
        ):
            raise ValidationError(
                _('Match participants can not be one team instance.')
            )

        if (
            self.score1 is not None
            and self.score2 is not None
            and self.score1 == self.score2
        ):
            raise ValidationError(_('Match scores can not be equals.'))

        return super().clean()

    @property
    def winner_loser(self) -> tuple[Optional[Team], Optional[Team]]:
        if self.status == self.StatusChoice.FINISHED:
            if self.score1 > self.score2:
                return (self.participant1, self.participant2)
            return (self.participant2, self.participant1)

        if self.status == self.StatusChoice.WALK_OVER:
            return (
                self.participant1 or self.participant2, None
            )
        
        return None
