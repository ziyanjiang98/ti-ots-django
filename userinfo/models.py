from django.db import models


# Create your models here.
class Engineer(models.Model):
    username = models.CharField(verbose_name="Engineer Username", max_length=32)
    password = models.CharField(verbose_name="password", max_length=64)
    email = models.EmailField(verbose_name="TI email", max_length=64)

    def __str__(self):
        return self.username + "(E:" + str(self.id) + ")"


class Supplier(models.Model):
    username = models.CharField(verbose_name="Supplier Username", max_length=32)
    password = models.CharField(verbose_name="password", max_length=64)
    email = models.EmailField(verbose_name="Company email", max_length=64)

    def __str__(self):
        return self.username + "(S:" + str(self.id) + ")"
