from django.db import models

class Session(models.Model):
    name = models.CharField(max_length=100, unique=True) 
    password = models.CharField(max_length=100, default="password")

    def __str__(self):
        return self.name


class Photo(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='photos/')