from django.urls import include, path

from . import views
from problem import views as problem_views
from submission import views as submission_views

urlpatterns = [
    path('', views.info, name='contest-info'),
    path('<int:contest_pk>/', views.info, name='contest-info'),
    path('<int:contest_pk>/ranking', views.ranking, name='contest-ranking'),
    path('<int:contest_pk>/problem/<int:problem_pk>', problem_views.problem_page, name='problem-page'),
    path('<int:contest_pk>/submit', submission_views.submit, name='submit-page'),
    path('<int:contest_pk>/submission/<int:sub_pk>', submission_views.submission, name='submission-page'),
]
