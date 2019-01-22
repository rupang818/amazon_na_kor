from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from localflavor.us.models import USStateField, USZipCodeField

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None # Don't use the username - instead, authenticate using email
    email = models.EmailField(_('email address'), unique=True)
    phone = models.IntegerField("Phone", default=12345678)
    address1 = models.CharField("Address line 1", max_length=1024, default='')
    address2 = models.CharField("Address line 2", max_length=1024, default='')
    city = models.CharField("City", max_length=1024, default='')
    state = USStateField()
    zip_code = USZipCodeField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'address1', 'first_name', 'last_name', 'city', 'state', 'zip_code']

    objects = UserManager()

    def __str__(self):
        return self.email