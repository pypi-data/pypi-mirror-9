from django.db import models


class One(models.Model):
    name = models.CharField(max_length=100)


class Two(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField(null=True, blank=True, default=0)


class Three(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField(null=True, blank=True, default=0)
