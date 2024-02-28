from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(unique=False, max_length=255)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(0.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
