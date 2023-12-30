from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import *
# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other")
        )

    email = models.EmailField(unique=True)
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=10, null=True, blank=True
    )
    age = models.IntegerField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

class SalesData(models.Model):
       date = models.DateField()
       product = models.CharField(max_length=100, blank=True, null=True)
       sales_number = models.CharField(max_length=100, blank=True, null=True)
       revenue = models.CharField(max_length=100, blank=True, null=True)
       file_name = models.ForeignKey('test_app.UploadedFile', on_delete=models.CASCADE)
       created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
       def __str__(self):
              return self.product
       
class UploadedFile(models.Model):
    file = models.FileField()
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.file.name
     
