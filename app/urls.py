from django.urls import path
from . import views

urlpatterns = [
    path('', views.go_to_show_files, name='go_to_show_files'),
    path('passwordResetRequestProcess/<str:token>/', views.passwordResetRequestProcess, name='passwordResetRequestProcess'),
    path('passwordResetRequest/', views.passwordResetRequestGet, name='passwordResetRequest'),
    path('shares/', views.shares, name='shares'),
    path('files/', views.show_files, name='show_files'),
    path('contacts/', views.show_contacts, name='contacts'),
    path('default/', views.default_pdf, name="default_pdf"),
    path('404/', views.page_not_found, name="page_not_found"),
    path('url/<token>/', views.url_mapping, name='url_mapping'),
]