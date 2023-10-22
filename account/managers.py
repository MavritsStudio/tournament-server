from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def _create_user(
        self, email, password, is_staff,
        is_superuser, **extra_fields,
    ):
        """
        Creates and saves a User with a given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff, is_active=True,
            is_superuser=is_superuser,
            last_login=now, date_joined=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class TeamManager(models.Manager):
    def filter_by_user(self, user):
        return self.get_queryset().filter(
            models.Q(mate1=user) | models.Q(mate2=user)
        )
