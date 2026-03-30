
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)

    def __str__(self):
        return self.store_name

class DigitalWallet(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Product(models.Model):
    STATUS_CHOICES = [('draft', 'مسودة'), ('published', 'منشور')]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

@receiver(post_save, sender=Supplier)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        DigitalWallet.objects.create(supplier=instance)
