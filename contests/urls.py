from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.info, name='contest-info'),
    path('<int:contest_id>/', views.info, name='contest-info'),
    path('login/', views.login_page, name='login-page'),
    path('logout/', views.logout_page, name='logout-page'),
    path('user/', views.user, name='auth'),
]
