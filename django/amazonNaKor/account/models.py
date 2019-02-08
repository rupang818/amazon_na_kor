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
    phone = models.IntegerField("Phone", default='')
    address1 = models.CharField("Address 1", max_length=1024, default='')
    address2 = models.CharField("Address 2", max_length=1024, default='', blank=True)
    city = models.CharField("City", max_length=1024, default='')
    state = USStateField(default='CA')  
    zip_code = USZipCodeField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name', 'address1', 'city', 'state', 'zip_code']

    objects = UserManager()

    def __str__(self):
        return self.email

class Recepient(models.Model):
    sender_email = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='sender_email')
    name = models.CharField("이름", max_length=1024, default='')
    phone = models.IntegerField("전화번호", default='')
    postal_code = models.IntegerField("우편번호", default='')
    address = models.CharField("주소", max_length=1024, default='')
    customs_id = models.CharField("통관고유호", max_length=1024, default='')

class Package(models.Model):
    sender_email = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='sender_email')
    recepient_id = models.IntegerField("받는사람 id")
    pkg_type = models.IntegerField("수업유형", default='1')
    width = models.FloatField("가로(cm)", default='10')
    length = models.FloatField("세로(cm)", default='10')
    height = models.FloatField("높이(cm)", default='10')
    weight = models.FloatField("중량(lb)", default='1')
    metric = models.IntegerField("중량단위", default='2')
    box_count = models.IntegerField("Box수량", default='1')
    standard_order = models.IntegerField("일반신청", default='0')

class Item(models.Model):
    sender_email = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='sender_email')
    recepient_id = models.IntegerField("받는사람 id")
    package_id = models.IntegerField("패키지 id")
    item_name = models.CharField("상품명", max_length=1024, default='')
    price = models.FloatField("단가 (USD)", default='0')
    qty = models.IntegerField("수량", default='1')

class Delivery(models.Model):
    class Meta:
        verbose_name_plural = "deliveries"

    payee = (
        ('SENDER', '송하인(sender) 납부'),
        ('RECEPIENT', '수취인 납부 (+ $5.00)'),
    )
    method = (
        ('DIRECT', '직접방문'),
        ('UPS', 'UPS 배송 (+ $10.00)'),
    )
    sender_email = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='sender_email')
    recepient_id = models.IntegerField("받는사람 id")
    package_id = models.IntegerField("패키지 id")
    item_id = models.IntegerField("아이템 id")
    customs_fee_payee = models.CharField("통관비 지불", choices=payee, max_length=1024, default='SENDER')
    method = models.CharField("패키지 전달 방법", choices=method, max_length=1024, default='DIRECT')
    agreement_signed = models.BooleanField("위 사항에 동의합니다")
    estimate = models.FloatField("Estimated Price")
    dropped_off = models.BooleanField(blank=True)
    sent = models.BooleanField(blank=True)
