from django.db import models


# Create your models here.
class Bid(models.Model):
    bid_price = models.FloatField(verbose_name="Bid Price")
    bid_datetime = models.DateTimeField(verbose_name="Bid Time")
    # Foreign Key
    order = models.ForeignKey(to="order.Order", on_delete=models.PROTECT, to_field="id")
    supplier = models.ForeignKey(to="userinfo.Supplier", on_delete=models.PROTECT, to_field="id")
