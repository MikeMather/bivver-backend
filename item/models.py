from django.db import models
from django.core.validators import MinValueValidator
from supplier.models import *


class Item(models.Model):
    name = models.CharField(max_length=150)
    order_by = models.CharField(max_length=20, default='Keg')
    quantity_per_order = models.PositiveIntegerField(default = 1, validators=[MinValueValidator(1)])
    MEASURE_CHOICES = (
        ('unit', 'unit'),
        ('millilitre', 'millilitre')
    )
    measure = models.CharField(
        max_length=10,
        choices=MEASURE_CHOICES,
        default='millilitre',
    )
    amount_per_unit = models.DecimalField(default=1.00, max_digits=9, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.DecimalField(default=0, max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    disabled = models.BooleanField(default=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, related_name='items', blank=True, default='')
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, default=None, blank=True)
    sku = models.CharField(max_length=50, null=True, blank=True, default='')
    image = models.CharField(max_length=1500, blank=True, default='')
    tasting_notes = models.CharField(max_length=500, blank=True, default='')
    style = models.CharField(max_length=50, blank=True, default='')
    serving_suggestions = models.CharField(max_length=500, blank=True, default='')
    alcohol_percentage = models.DecimalField(max_digits=4, decimal_places=3, validators=[MinValueValidator(0)], blank=True, default=0)
    description = models.CharField(max_length=500, blank=True, default='')
    barcode = barcode = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        db_table = 'items'
        unique_together = ('supplier', 'sku')

    def __str__(self):
        return self.name