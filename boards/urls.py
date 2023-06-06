from django.urls import path, re_path
from . import views

urlpatterns = [
      path(r'u/<username>', views.RunnerDetailView.as_view(), name='profile'),
   path(r'<slug:level>/<int:mnum>', views.MissionLeaderboardView.as_view(), name='mission'),
    path('levels', views.MissionListView.as_view(), name='levels'),
    path('', views.MissionListView.as_view(), name='index'),

]