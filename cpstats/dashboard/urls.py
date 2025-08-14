from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path('',views.index, name = 'index'),
    path('cf_ajax/', views.cf_ajax, name='cf_ajax'),
    path('lc_ajax/', views.lc_ajax, name='lc_ajax'),
    path('cc_ajax/', views.cc_ajax, name='cc_ajax'),
    path('at_ajax/', views.at_ajax, name='at_ajax'),
]
