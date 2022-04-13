import json
from datetime import datetime, date

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.http import FileResponse
from django.shortcuts import render, HttpResponse, redirect
from order.models import Template, Order, OrderCandidate
from ots.utils import BootstrapForm, BootstrapModelForm, add_session_msg
from userinfo.models import Supplier
from quote.models import Bid


# Create your views here.
class TemplateModelForm(BootstrapModelForm):
    class Meta:
        model = Template
        fields = ["template_name", "template_json", "creator"]
        widgets = {
            "template_name": forms.TextInput(),
            "creator": forms.HiddenInput(),
        }

    def clean_template_name(self):
        input_template_name = self.cleaned_data.get("template_name")
        if Template.objects.filter(template_name=input_template_name).first() is not None:
            raise ValidationError("repeated template name")
        return input_template_name


def create_template(request, *args, **kwargs):
    user_id = request.session.get("info")["id"]
    form = TemplateModelForm(initial={"creator": user_id})
    if request.method == "GET":
        return render(request, "create_template.html", {"form": form})
    form = TemplateModelForm(request.POST)
    if form.is_valid():
        form.save()
        add_session_msg(request, "success", "successfully create new template")
        return redirect("/engineer/order/template-list/")
    return render(request, "create_template.html", {"form": form, "msgs": kwargs["msgs"]})


def template_list(request, *args, **kwargs):
    result_list = Template.objects.all()
    return render(request, "template_list.html", {"template_list": result_list, "msgs": kwargs["msgs"]})


def delete_template(request, *args, **kwargs):
    template_id = request.GET.get("tid")
    if template_id:
        try:
            Template.objects.filter(id=template_id).delete()
            add_session_msg(request, "success", "successfully delete template")
            return redirect("/engineer/order/template-list/")
        except ProtectedError:
            add_session_msg(request, "danger", "this template is related to in-process business")
            return redirect("/engineer/order/template-list/")
    add_session_msg("danger", "illegal request")
    return redirect("/engineer/order/template-list/")


class OrderModelForm(BootstrapModelForm):
    class Meta:
        model = Order
        fields = ["order_name", "order_date", "order_amount", "template", "creator", "order_status"]
        widgets = {
            "creator": forms.HiddenInput(),
            "order_status": forms.HiddenInput(),
            'order_date': forms.DateInput(format='%m/%d/%Y',
                                          attrs={'class': 'form-control', 'placeholder': 'Select a date',
                                                 'type': 'date'}),
        }

    def clean_order_date(self):
        input_order_date = self.cleaned_data.get("order_date")
        today_date = date.today()
        if input_order_date <= today_date:
            raise ValidationError("date is earlier than today")
        return input_order_date

    def clean_order_amount(self):
        input_order_amount = self.cleaned_data.get("order_amount")
        if input_order_amount <= 0:
            raise ValidationError("illegal order amount")
        return input_order_amount

    def clean_order_name(self):
        input_order_name = self.cleaned_data.get("order_name")
        if Order.objects.filter(order_name=input_order_name).first() is not None:
            raise ValidationError("repeated order name")
        return input_order_name


def create_order(request, *args, **kwargs):
    user_id = request.session.get("info")["id"]
    form = OrderModelForm(initial={"creator": user_id, "order_status": 1})
    if request.method == "GET":
        return render(request, "create_order.html", {"form": form})
    form = OrderModelForm(request.POST)
    if form.is_valid():
        form.save()
        add_session_msg(request, "success", "successfully create order")
        return redirect("/engineer/order/order-list/")
    return render(request, "create_order.html", {"form": form, "msgs": kwargs["msgs"]})


def order_list(request, *args, **kwargs):
    result_list = Order.objects.all()
    return render(request, "order_list.html", {"order_list": result_list, "msgs": kwargs["msgs"]})


def order_detail(request, *args, **kwargs):
    order_id = request.GET.get("oid")
    query_set = Order.objects.filter(id=order_id)
    if query_set.count() != 1:
        redirect("/order/order-list/")
    order = query_set.first()
    order_candidate = OrderCandidate.objects.filter(order=order_id).all()
    candidate_list = []
    for item in order_candidate:
        candidate_list.append(item.candidate)
    supplier_list = Supplier.objects.all()
    return render(request, "order_detail.html", {"order": order,
                                                 "candidate_list": candidate_list,
                                                 "supplier_list": supplier_list,
                                                 "msgs": kwargs["msgs"]
                                                 })


def add_candidate(request, *args, **kwargs):
    order_id = request.POST.get("oid")
    supplier_id = request.POST.get("sid")
    if order_id is None or supplier_id is None:
        add_session_msg(request, "danger", "supplier not exist")
        return redirect("/engineer/order/order-detail?oid=" + str(order_id))
    order_id = int(order_id)
    supplier_id = int(supplier_id)
    order = Order.objects.filter(id=order_id).first()
    supplier = Supplier.objects.filter(id=supplier_id).first()
    if order is None or supplier is None:
        add_session_msg(request, "danger", "unknown order or supplier")
        return redirect("/engineer/order/order-list/")
    if order.order_status > 2:
        add_session_msg(request, "danger", "illegal order status")
        return redirect("/engineer/order/order-detail?oid=" + str(order_id))
    if OrderCandidate.objects.filter(order=order_id, candidate=supplier_id).count() < 1:
        OrderCandidate.objects.create(order=order, candidate=supplier)
        order.order_status = 2
        order.save()
        add_session_msg(request, "success", "successfully add supplier to candidate list")
    else:
        add_session_msg(request, "danger", "supplier already in candidate list")
    return redirect("/engineer/order/order-detail?oid=" + str(order_id))


def delete_candidate(request, *args, **kwargs):
    order_id = int(request.GET.get("oid"))
    supplier_id = int(request.GET.get("sid"))
    order = Order.objects.filter(id=order_id).first()
    supplier = Supplier.objects.filter(id=supplier_id).first()
    if order is None or supplier is None:
        add_session_msg(request, "danger", "unknown order or supplier")
        return redirect("/engineer/order/order-detail?oid=" + str(order_id))
    if order.order_status != 2:
        add_session_msg(request, "danger", "illegal order status")
        return redirect("/engineer/order/order-detail?oid=" + str(order_id))
    try:
        OrderCandidate.objects.get(order=order, candidate=supplier).delete()
    except ProtectedError:
        add_session_msg(request, "danger", "this candidate is related to in-process business")
        return redirect("/engineer/order/order-detail?oid=" + str(order_id))
    if OrderCandidate.objects.filter(order=order).count() == 0:
        add_session_msg(request, "success", "successfully delete, status return to NEW because of none candidates")
        order.order_status = 1
        order.save()
    else:
        add_session_msg(request, "success", "successfully delete")
    return redirect("/engineer/order/order-detail?oid=" + str(order_id))


def push_to_quote(request, *args, **kwargs):
    order_id = request.GET.get("oid")
    order = Order.objects.filter(id=order_id).first()
    if order is not None and order.order_status == 2:
        order.order_status = 3
        order.save()
        add_session_msg(request, "success", "successfully push to quote")
    else:
        add_session_msg(request, "danger", "fail to push to quote")
    return redirect("/engineer/order/order-list/")


def order_bid_list(request, *args, **kwargs):
    order_id = request.GET.get("oid")
    order = Order.objects.filter(id=order_id).first()
    if order is not None:
        bid_query_set = Bid.objects.filter(order=order_id)
        return render(request, "order_bid_list.html", {"bid_list": bid_query_set, "msgs": kwargs["msgs"]})
    else:
        add_session_msg(request, "danger", "illegal request")
    return redirect("/engineer/order/order-list/")


def finish_quote(request, *args, **kwargs):
    order_id = request.GET.get("oid")
    order = Order.objects.filter(id=order_id).first()
    if order is not None and order.order_status == 3:
        bid_list = []
        bid_query_set = Bid.objects.filter(order=order_id)
        min_price = float("inf")
        for item in bid_query_set:
            if item.bid_price < min_price:
                bid_list.clear()
                min_price = item.bid_price
                bid_list.append(item)
            elif item.bid_price == min_price:
                bid_list.append(item)
        if len(bid_list) == 0:
            add_session_msg(request, "danger", "not legal bid, order is push back to READY status")
            order.order_status = 2
            order.save()
            return redirect("/engineer/order/order-list/")
        final_bid = None
        for item in bid_list:
            if final_bid is None:
                final_bid = item
                continue
            if final_bid.bid_datetime > item.bid_datetime:
                final_bid = item
        order.order_status = 4
        order.supplier = final_bid.supplier
        order.save()
        add_session_msg(request, "success", "successfully finish quote")
    else:
        add_session_msg(request, "danger", "illegal order status")
    return redirect("/engineer/order/order-list/")


def finish_order(request, *args, **kwargs):
    order_id = request.GET.get("oid")
    order = Order.objects.filter(id=order_id).first()
    if order is not None and order.order_status == 5:
        order.order_status = 6
        order.save()
        add_session_msg(request, "success", "order is finished")
    else:
        add_session_msg(request, "danger", "illegal request")
    return redirect("/engineer/order/order-list/")


def deny_order(request, *args, **kwargs):
    order_id = request.GET.get("oid")
    order = Order.objects.filter(id=order_id).first()
    if order is not None and order.order_status == 5:
        order.order_status = 4
        order.save()
        add_session_msg(request, "info", "order is denied and back to manufacture")
    else:
        add_session_msg(request, "danger", "illegal request")
    return redirect("/engineer/order/order-list/")


def download_file(request, *args, **kwargs):
    order_id = request.GET.get("oid")
    try:
        file_name = order_id + ".pdf"
        file = open("media/order_file/" + file_name, 'rb')
    except FileNotFoundError:
        return HttpResponse("file not exists")
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=' + file_name
    return response
