from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=1)


class Customer(models.Model):
    name = models.CharField(max_length=1)
