import datetime
import pytz
import os

from django.core.exceptions import ValidationError
from django.shortcuts import render, HttpResponse, redirect

from order.models import Order, OrderCandidate
from ots.utils import BootstrapForm, add_session_msg
from quote.models import Bid
from userinfo.models import Supplier
from django import forms


# Create your views here.
def quote_list(request, *args, **kwargs):
    user_id = request.session.get("info")["id"]
    order_candidate_list = OrderCandidate.objects.filter(candidate=user_id)
    order_list = []
    for item in order_candidate_list:
        if item.order.order_status == 3:
            order_list.append(item.order)
    return render(request, "quote_list.html", {"order_list": order_list})


class BidForm(BootstrapForm):
    bid_price = forms.FloatField(min_value=0)
    order_id = forms.CharField(widget=forms.HiddenInput())

    def clean_bid_price(self):
        input_bid_price = self.cleaned_data.get("bid_price")
        if input_bid_price <= 0:
            raise ValidationError("illegal price")
        return input_bid_price


def bid_on_order(request, *args, **kwargs):
    user_id = request.session.get("info")["id"]
    if request.method == "GET":
        order_id = request.GET.get("oid")
        order = Order.objects.filter(id=order_id).first()
        bid = Bid.objects.filter(order_id=order_id, supplier_id=user_id).first()
        if order is not None:
            form = BidForm(initial={"order_id": order_id})
            return render(request, "bid_on_order.html", {"order": order,
                                                         "form": form,
                                                         "bid": bid,
                                                         "msgs": kwargs["msgs"]})
        add_session_msg(request, "danger", "illegal request")
        return redirect("/quote/quote-list/")
    form = BidForm(request.POST)
    if form.is_valid():
        order_id = form.cleaned_data.get("order_id")
        order = Order.objects.filter(id=order_id).first()
        supplier = Supplier.objects.filter(id=user_id).first()
        current_time = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles"))
        Bid.objects.update_or_create(defaults={"bid_price": form.cleaned_data.get("bid_price"),
                                               "bid_datetime": current_time},
                                     order=order,
                                     supplier=supplier)
        add_session_msg(request, "success", "successfully bid on the order")
        return redirect("/supplier/quote/bid-on-order?oid=" + str(order.id))
    else:
        order_id = request.POST.get("order_id", "0")
        order = Order.objects.filter(id=order_id).first()
        bid = Bid.objects.filter(order_id=order_id, supplier_id=user_id).first()
        if order is not None:
            return render(request, "bid_on_order.html", {"order": order,
                                                         "form": form,
                                                         "bid": bid,
                                                         "msgs": kwargs["msgs"]})
        return redirect("/supplier/quote/bid-on-order?oid=" + order_id)


class FileUploadForm(forms.Form):
    order_file = forms.FileField()
    order_id = forms.CharField(widget=forms.HiddenInput())

    def clean_order_file(self):
        input_order_file = self.cleaned_data.get("order_file")
        input_order_file_name = input_order_file.name
        if not str.endswith(input_order_file_name, ".pdf"):
            raise ValidationError("pdf format required")
        return input_order_file

    def clean(self):
        input_order_file = self.cleaned_data.get("order_file")
        input_order_file_name = input_order_file.name
        order_id = self.cleaned_data.get("order_id")
        if not input_order_file_name == str(order_id) + ".pdf":
            raise ValidationError("order_id.pdf name required")
        return self.cleaned_data


def my_order(request, *args, **kwargs):
    user_id = request.session.get("info")["id"]
    order_query_set = Order.objects.filter(supplier_id=user_id)
    combined_list = []
    for item in order_query_set:
        form = FileUploadForm(initial={"order_id": item.id})
        combined_list.append([item, form])
    return render(request, "my_order.html", {"combined_list": combined_list, "msgs": kwargs["msgs"]})


def upload_file(request, *args, **kwargs):
    form = FileUploadForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        order_id = form.cleaned_data.get("order_id")
        order = Order.objects.filter(id=order_id).first()
        if order is not None and order.order_status in [4, 5]:
            order_file_object = form.cleaned_data.get("order_file")
            order_file_path = os.path.join("media", "order_file", order_file_object.name)
            f = open(order_file_path, mode="wb")
            for chunk in order_file_object.chunks():
                f.write(chunk)
            f.close()
            order.order_file = order_file_path
            order.order_status = 5
            order.save()
            add_session_msg(request, "success", "successfully upload file")
        else:
            add_session_msg(request, "danger", "illegal order status")
        return redirect("/supplier/quote/my-order/")
    else:
        add_session_msg(request, "danger", "illegal format")
    return redirect("/supplier/quote/my-order/")
