from string import digits
from functools import partial
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string

from utils.utils import get_uuid_hex

from account.managers import UserManager, TeamManager


class User(AbstractUser):
    username = None

    uid = models.CharField(
        _('uid'), max_length=6, primary_key=True,
        default=partial(get_random_string, length=6, allowed_chars=digits),
    )

    email = models.EmailField(_("email address"), unique=True)

    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    middle_name = models.CharField(
        _('middle name'), max_length=150, blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self) -> str:
        return ' '.join(filter(
            bool,
            [self.first_name, self.middle_name, self.last_name],
        ))


class Team(models.Model):
    code = models.CharField(
        _('code'), max_length=32,
        primary_key=True, default=get_uuid_hex,
    )

    name = models.CharField(_('name'), max_length=12, unique=True)
    description = models.TextField(
        _('description'), max_length=256, blank=True,
    )

    mate1 = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL,
        verbose_name=_('owner'), null=True,
        related_name='owned_teams',
    )
    mate2 = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL,
        verbose_name=_('member'), null=True,
        related_name='mated_teams',
    )

    created = models.DateTimeField(_('date created'), auto_now_add=True)

    objects = TeamManager()

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        unique_together = ['mate1', 'mate2']

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.mate1 == self.mate2:
            raise ValidationError(
                _('Team mates can not be one user instance.'),
            )

        return super().clean()

    @property
    def mates(self) -> list[get_user_model()]:
        return [self.mate1, self.mate2]

    @property
    def is_active(self) -> bool:
        """Team is inactive if any of the mates is `None`."""
        return bool(self.mate1 and self.mate2)
