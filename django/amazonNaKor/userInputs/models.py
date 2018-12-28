from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, URLValidator

# Create your models here.

class InvoiceForm(models.Model):
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	
	# Sender info
	sender_name = models.CharField(max_length=100)
	sender_address = models.TextField(max_length=150)
	sender_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

	# Receiver info
	receiver_name = models.CharField(max_length=100)
	receiver_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
	receiver_postal_code = models.PositiveIntegerField(default=15987, validators=[MinValueValidator(1)], max_length=5)
	receiver_address = models.CharField(max_length=150)
	receiver_detail_address = models.CharField(max_length=100)
	customs_id = models.CharField(max_length=10)

	# Package info
	item_url = models.TextField(validators=[URLValidator()])
	width = models.DecimalField(max_digits=40, decimal_places=3)
	length = models.DecimalField(max_digits=40, decimal_places=3)
	height = models.DecimalField(max_digits=40, decimal_places=3)
	weight = models.DecimalField(max_digits=40, decimal_places=3)
	box_qty = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

	# Item info (EN)
	item_name = models.CharField(max_length=100)
	transit_memo = models.CharField(default='', max_length=100)
	item_price = models.DecimalField(max_digits=6, decimal_places=2)
	item_qty = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

	# Invoice info
	final_price = models.DecimalField(max_digits=6, decimal_places=2)
