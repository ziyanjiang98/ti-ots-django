"""ots URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings

import order.views
import quote.views
import userinfo.views

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}, name='media'),
    # common urls
    path('', userinfo.views.login),
    path('login/', userinfo.views.login),
    path('logout/', userinfo.views.logout),
    path('', userinfo.views.login),
    # engineer register url
    path('engineer/register/', userinfo.views.engineer_register),
    # engineer index url
    path('engineer/index/', userinfo.views.engineer_index),
    # userinfo urls
    path('engineer/userinfo/user-list/', userinfo.views.user_list),
    path('engineer/userinfo/delete-user/', userinfo.views.delete_user),
    # order urls
    path('engineer/order/create-template/', order.views.create_template),
    path('engineer/order/template-list/', order.views.template_list),
    path('engineer/order/delete-template/', order.views.delete_template),
    path('engineer/order/create-order/', order.views.create_order),
    path('engineer/order/order-list/', order.views.order_list),
    path('engineer/order/add-candidate/', order.views.add_candidate),
    path('engineer/order/delete-candidate/', order.views.delete_candidate),
    path('engineer/order/order-detail/', order.views.order_detail),
    path('engineer/order/start-quote/', order.views.push_to_quote),
    path('engineer/order/finish-quote/', order.views.finish_quote),
    path('engineer/order/order-bid-list/', order.views.order_bid_list),
    path('engineer/order/finish-order/', order.views.finish_order),
    path('engineer/order/deny-order/', order.views.deny_order),

    # supplier register
    path('supplier/register/', userinfo.views.supplier_register),
    # supplier index url
    path('supplier/index/', userinfo.views.supplier_index),

    # quote
    path('supplier/quote/quote-list/', quote.views.quote_list),
    path('supplier/quote/bid-on-order/', quote.views.bid_on_order),
    path('supplier/quote/my-order/', quote.views.my_order),
    path('supplier/quote/upload-file/', quote.views.upload_file),

    # file
    path('supplier/download-file/', order.views.download_file),
    path('engineer/download-file/', order.views.download_file),
]
