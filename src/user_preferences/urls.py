from django.urls import path

from . import views

urlpatterns = [
    path('images/<str:image>', views.user_image, name='user_image'),
]
