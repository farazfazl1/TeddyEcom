from django.urls import path
from category import views

app_name = "category"

urlpatterns = [
    path('', views.category, name='category')
]
