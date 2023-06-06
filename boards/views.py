from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from boards.models import *

class MissionListView(ListView):

    model=Mission
    template_name = 'level_list.html'
    def get_queryset(self):
        return Mission.objects.all().order_by('level','mnum')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



class MissionLeaderboardView(DetailView):

    model = Mission
    template_name = "level_board.html"
    context_object_name = 'mission'
    def get_object(self, queryset=None):
        level_id = self.kwargs['level'].upper()
        mnum = self.kwargs['mnum']
        return Mission.objects.get(level=level_id,mnum=mnum)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        runs = Run.objects.filter(mission=context['object'],is_obsolete=False,has_vid=True).order_by('time_s')
        ranks = rank_times_min([r.time_s for r in runs])
        context['runs'] = list(zip(runs, ranks))
        return context

class RunnerDetailView(DetailView):
    model = Runner
    template_name = "runnerprofile.html"
    context_object_name = 'runner'

    def get_object(self, queryset=None):
        uname = self.kwargs['username']
        runners_possible = Runner.objects.filter(tsc_as_primary=False,src_username__iexact=uname)
        if runners_possible.exists():
            return runners_possible.first()
        runners_possible = Runner.objects.filter(tsc_username__iexact=uname)
        if runners_possible.exists():
            return runners_possible.first()
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        runs = Run.objects.filter(runner=context['object']).order_by('-date_performed')
        context['runs'] = runs
        context['totalranks'] = context['object'].get_mission_ranks()
        return context