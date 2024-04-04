from django.urls import path, re_path
from . import views

urlpatterns = [
      path(r'u/<username>', views.RunnerDetailView.as_view(), name='profile'),
path(r'ranks/<int:mnum>', views.RunnerRankingView.as_view(), name='ranks'),
    path(r'ranks', views.RunnerRankingView.as_view(), kwargs={'mnum': 0}, name='ranks'),
    path(r'ranks/boss', views.RunnerRankingView.as_view(), kwargs={'mnum': 6}, name='ranks'),
   path(r'<slug:level>/<int:mnum>', views.MissionLeaderboardView.as_view(), name='mission'),
    path('levels', views.MissionListView.as_view(), name='levels'),

    path('', views.MissionListView.as_view(), name='index'),

]