# @File  : urls.py
# @Author: wsc
# @Date  : 2019/8/7
# @Desc  :
from django.conf.urls import url

from apps import views

urlpatterns = [
    url(r'^validate', views.r_validate),
]
