from django.urls import include, path

from . import views
from problem import views as problem_views

urlpatterns = [
    path('', views.info, name='contest-info'),
    path('<int:contest_id>/', views.info, name='contest-info'),
    path('<int:contest_id>/<int:pk>', problem_views.problem_page, name='problem-page'),
    path('accounts/login/', views.login_page, name='login-page'),
    path('logout/', views.logout_page, name='logout-page'),
]
