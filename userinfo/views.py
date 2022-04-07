from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.shortcuts import render, HttpResponse, redirect

from ots.utils import BootstrapForm, BootstrapModelForm, add_session_msg
from userinfo.models import Supplier, Engineer
from django import forms


class LoginForm(BootstrapForm):
    username = forms.CharField(label="username",
                               widget=forms.TextInput())
    password = forms.CharField(label="password",
                               widget=forms.PasswordInput(render_value=True))
    usertype = forms.ChoiceField(label="usertype",
                                 choices=(("", "--select--"), ("engineer", "engineer"), ("supplier", "supplier")))


def login(request, *args, **kwargs):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data)
            form_data = form.cleaned_data
            user = None
            usertype = form_data["usertype"]
            if usertype == "engineer":
                table = Engineer
                user = table.objects.filter(username=form_data["username"], password=form_data["password"]).first()
            elif usertype == "supplier":
                table = Supplier
                user = table.objects.filter(username=form_data["username"], password=form_data["password"]).first()
            if user is not None:
                request.session["info"] = {"username": user.username,
                                           "usertype": usertype,
                                           "id": user.id}
                request.session.set_expiry(300)
                return redirect("/" + usertype + "/index/")
            form.add_error("password", "incorrect username or password")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form, "msgs": kwargs["msgs"]})


def logout(request, *args, **kwargs):
    request.session.clear()
    add_session_msg(request, "success", "successfully logout")
    return redirect("/login/")


class EngineerRegisterModelForm(BootstrapModelForm):
    re_password = forms.CharField(label="Confirmed Password", required=True, widget=forms.PasswordInput())

    class Meta:
        model = Engineer
        fields = ["username", "password", "re_password", "email"]
        widgets = {
            "username": forms.TextInput(),
            "password": forms.PasswordInput(),
            "email": forms.TextInput(),
        }

    def clean_email(self):
        user_email = self.cleaned_data.get("email")
        if not str.endswith(user_email, "@ti.com"):
            raise ValidationError("TI email required")
        if Engineer.objects.filter(email=user_email).first() is not None:
            raise ValidationError("repeated email")
        return user_email

    def clean_username(self):
        input_username = self.cleaned_data.get("username")
        if Engineer.objects.filter(username=input_username).first() is not None:
            raise ValidationError("repeated username")
        return input_username

    def clean(self):
        if self.cleaned_data.get("re_password") != self.cleaned_data.get("password"):
            self.add_error('re_password', 'passwords unmatched')
            raise ValidationError("passwords unmatched")
        return self.cleaned_data


def engineer_register(request, *args, **kwargs):
    form = EngineerRegisterModelForm()
    if request.method == "GET":
        return render(request, "engineer_register.html", {"form": form})
    form = EngineerRegisterModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        add_session_msg(request, "success", "Successfully registered, please login")
        return redirect("/login/")
    return render(request, "engineer_register.html", {"form": form, "msgs": kwargs["msgs"]})


class SupplierRegisterModelForm(BootstrapModelForm):
    re_password = forms.CharField(label="Confirmed Password", widget=forms.PasswordInput(), required=True)

    class Meta:
        model = Supplier
        fields = ["username", "password", "re_password", "email"]
        widgets = {"password": forms.PasswordInput}

    def clean_email(self):
        user_email = self.cleaned_data.get("email")
        if Supplier.objects.filter(email=user_email).first() is not None:
            raise ValidationError("repeated email")
        return user_email

    def clean_username(self):
        input_username = self.cleaned_data.get("username")
        if Supplier.objects.filter(username=input_username).first() is not None:
            raise ValidationError("repeated username")
        return input_username

    def clean(self):
        if self.cleaned_data.get("re_password") != self.cleaned_data.get("password"):
            self.add_error('re_password', 'passwords unmatched')
            raise ValidationError("passwords unmatched")
        return self.cleaned_data


def supplier_register(request, *args, **kwargs):
    form = SupplierRegisterModelForm()
    if request.method == "GET":
        return render(request, "supplier_register.html", {"form": form})
    form = SupplierRegisterModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        add_session_msg(request, "success", "Successfully registered, please login")
        return redirect("/login/")
    return render(request, "engineer_register.html", {"form": form, "msgs": kwargs["msgs"]})


def engineer_index(request, *args, **kwargs):
    return render(request, "engineer_index.html", {"msgs": kwargs["msgs"]})


def supplier_index(request, *args, **kwargs):
    return render(request, "supplier_index.html", {"msgs": kwargs["msgs"]})


def user_list(request, *args, **kwargs):
    user_type = request.GET.get("type", "engineer")
    result_list = None
    if user_type == "engineer":
        result_list = Engineer.objects.all()
    elif user_type == "supplier":
        result_list = Supplier.objects.all()
    return render(request, "user_list.html", {"user_list": result_list, "user_type": user_type, "msgs": kwargs["msgs"]})


def delete_user(request, *args, **kwargs):
    user_type = request.GET.get("type")
    user_id = request.GET.get("uid")
    if user_type and user_id:
        if user_type == "engineer":
            user_table = Engineer
        elif user_type == "supplier":
            user_table = Supplier
        else:
            add_session_msg(request, "danger", "illegal request")
            return redirect("/engineer/userinfo/user-list?type=" + user_type)
        try:
            user_table.objects.get(id=user_id).delete()
        except ProtectedError:
            add_session_msg(request, "danger", "this user is related to in-process business")
            return redirect("/engineer/userinfo/user-list?type=" + user_type)
        add_session_msg(request, "success", "successfully delete")
        return redirect("/engineer/userinfo/user-list?type=" + user_type)
