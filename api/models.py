from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
      
        db_table = "categories"


class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        
        db_table = "locations"


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20)  # lost / found
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        
        db_table = "items"