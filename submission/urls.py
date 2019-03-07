from django.urls import path
from . import views

urlpatterns = [
    path('<int:contest_pk>/testsubmit', views.test_submit, name='test-submit'),
    path('detail/<int:pk>', views.detail, name='submission-detail'),
]
