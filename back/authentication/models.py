from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    username = None
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []
