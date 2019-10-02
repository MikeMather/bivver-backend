from django.db import models
from django.conf import settings

class Client(models.Model):
    name = models.CharField(max_length=300)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    licensee_number = models.CharField(max_length=300, blank=True)
    image = models.CharField(max_length=150, blank=True, default='')

    class Meta:
        db_table = 'clients'
