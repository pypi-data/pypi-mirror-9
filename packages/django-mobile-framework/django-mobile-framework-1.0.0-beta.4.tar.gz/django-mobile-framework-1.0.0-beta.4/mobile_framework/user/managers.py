from django.db import models
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def _create_user(self, username, password, **kwargs):
        if not password:
            raise ValueError('Users must have a password.')
        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **kwargs):
        """ Creates a new user. """
        return self._create_user(username, password, **kwargs)

    def create_superuser(self, username, password, **kwargs):
        """ Creates a new superuser. """
        user = self._create_user(username, password, **kwargs)
        user.is_admin = True
        user.save(using=self._db)
        return user