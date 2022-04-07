from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect, render


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        url = request.path_info
        if url == "/login/" or url == "/logout/" or url == "/engineer/register/" or url == "/supplier/register/":
            return
        info = request.session.get("info")
        if not info:
            request.session["msgs"] = [{"type": "danger", "content": "Please login"}, ]
            return redirect("/login/")
        usertype = info["usertype"]
        request_type = url.split("/")[1]
        if request_type == 'media':
            return
        if usertype == request_type:
            return
        return redirect("/" + usertype + "/" + "index/")
