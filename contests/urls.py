from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.info, name='contest-info'),
    path('<int:contest_id>/', views.info, name='contest-info'),
]
