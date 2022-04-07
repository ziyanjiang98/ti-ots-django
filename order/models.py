from django.db import models


# Create your models here.
class Template(models.Model):
    template_name = models.CharField(max_length=32)
    template_json = models.JSONField(max_length=64)
    # Foreign Key
    creator = models.ForeignKey(to="userinfo.Engineer", on_delete=models.PROTECT, to_field="id")

    def __str__(self):
        return self.template_name


class Order(models.Model):
    # <td>{{ infor.updatetime|date:"Y-m-d H:i:s" }}</td>
    order_name = models.CharField(max_length=32)
    order_amount = models.IntegerField()
    order_date = models.DateField()
    # 1-new, 2-ready, 3-quote, 4-manufacture, 5-waiting, 6-finished
    order_status = models.IntegerField()
    order_file = models.CharField(max_length=128)
    # Foreign Key
    creator = models.ForeignKey(to="userinfo.Engineer", on_delete=models.PROTECT, to_field="id")
    template = models.ForeignKey(to="order.Template", on_delete=models.PROTECT, to_field="id")
    supplier = models.ForeignKey(to="userinfo.Supplier", on_delete=models.PROTECT, to_field="id",
                                    null=True, blank=True)

    def __str__(self):
        return self.order_name


class OrderCandidate(models.Model):
    order = models.ForeignKey(to="order.Order", on_delete=models.PROTECT, to_field="id")
    candidate = models.ForeignKey(to="userinfo.Supplier", on_delete=models.PROTECT, to_field="id")
