from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from utils.constants import SUPPLIER_TYPES


class Supplier(models.Model):
    name = models.CharField(max_length=300)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_payment_term = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    keg_deposit_price = models.DecimalField(max_digits=32, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    image = models.CharField(max_length=150, blank=True, default='')
    supplier_type = models.CharField(max_length=150, choices=SUPPLIER_TYPES.CHOICES, default=SUPPLIER_TYPES.CHOICES[0][0])

    class Meta:
        db_table = 'suppliers'
