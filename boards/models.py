from django.db import models
from django.contrib.auth.models import User
from datetime import datetime as dt
import re

TIME_SOURCE_CHOICES = [
    ('TSC', 'SONICCENTER'),
    ('SRC', 'SPEEDRUN.COM'),
]



POINTS_OVERALL = 0
POINTS_M1 = 1
POINTS_M2 = 2
POINTS_M3 = 3
POINTS_M4 = 4
POINTS_M5 = 5
POINTS_BOSS = 6
LEVEL_CHOICES = [('CE', 'City Escape'), ('WC', 'Wild Canyon'), ('PL', 'Prison Lane'), ('MHA', 'Metal Harbor'), ('GF', 'Green Forest'), ('PH', 'Pumpkin Hill'), ('MST', 'Mission Street'), ('AM', 'Aquatic Mine'), ('101', 'Route 101'), ('HB', 'Hidden Base'), ('PC', 'Pyramid Cave'), ('DC', 'Death Chamber'), ('EE', 'Eternal Engine'), ('MHE', 'Meteor Herd'), ('CG', 'Crazy Gadget'), ('FR', 'Final Rush'), ('IG', 'Iron Gate'), ('DL', 'Dry Lagoon'), ('SO', 'Sand Ocean'), ('RH', 'Radical Highway'), ('EQ', 'Egg Quarters'), ('LC', 'Lost Colony'), ('WB', 'Weapons Bed'), ('SH', 'Security Hall'), ('WJ', 'White Jungle'), ('280', 'Route 280'), ('SR', 'Sky Rail'), ('MSP', 'Mad Space'), ('CW', 'Cosmic Wall'), ('FC', 'Final Chase'), ('CC', 'Cannon\'s Core'), ('GH', 'Green Hill')]
BOSS_CHOICES = [('BF', 'Big Foot'), ('EGG1', 'Eggman 1'), ('SH1', 'Shadow 1'), ('KBB', 'King Boom Boo'), ('EGH', 'Egg Golem (Hero)'), ('RG', 'Rouge'), ('EGG2', "Eggman 2"), ('SH2','Shadow 2'), ('HS', 'Hot Shot'), ('T1', 'Tails 1'), ('FD', 'Flying Dog'), ('SO1','Sonic 1'), ('EGD', 'Egg Golem (Dark)'), ('KN', 'Knuckles'), ('T2', 'Tails 2'), ('SO2', 'Sonic 2'), ('BL', 'Biolizard'), ('FH', 'Finalhazard')]
URL_REGEX = re.compile('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+')
IMG_EXT = ["gif","png","jpg"]


def rank_times_min(times):
    res = [0]*len(times)
    curr_streak = 0
    for i in range(len(times)):
        if i == 0:
            res[i] = 1
            continue
        elif times[i-1] == times[i]:
            curr_streak += 1
            res[i] = i + 1 - curr_streak
        else:
            res[i] = i + 1
            curr_streak = 0
    return res

def get_runner_haspoints():
    return Runner.objects.filter(points_overall__gt=0)

class Runner(models.Model):
    #we'll get some more stuff here
    id = models.IntegerField(primary_key=True)
    tsc_username = models.TextField(blank=True)
    src_username = models.TextField(blank=True)
    tsc_as_primary = models.BooleanField(default=False)
    points_overall = models.IntegerField(default=0)
    points_m1 = models.IntegerField(default=0)
    points_m2 = models.IntegerField(default=0)
    points_m3 = models.IntegerField(default=0)
    points_m4 = models.IntegerField(default=0)
    points_m5 = models.IntegerField(default=0)
    points_boss = models.IntegerField(default=0)

    @property
    def username(self):
        if self.tsc_as_primary or self.src_username == "":
            return self.tsc_username
        else:
            return self.src_username
    def get_all_runs(self,obsolete=False,vidonly=True):
        runs = Run.objects.filter(runner=self, is_obsolete=obsolete).order_by('-date_performed')
        if not vidonly:
            return runs
        else:
            run_ids = [run.id for run in runs if run.has_video]
            return Run.objects.filter(id__in=run_ids).order_by('-date_performed')
    def recalculate_allpoints(self):
        overall = 0
        for i in range(1,6):
            setattr(self,f"points_m{i}", self.compute_points(i))
            overall += getattr(self,f"points_m{i}")
        bosspoints = self.compute_points(POINTS_BOSS)
        overall += bosspoints
        self.points_boss = bosspoints
        self.points_overall = overall


    def compute_points(self,pts_type=POINTS_OVERALL):
        all_user_runs = self.get_all_runs()
        m_objs = Mission.objects.all()
        if pts_type == POINTS_BOSS:
            m_objs = Mission.objects.filter(is_boss=True)
        elif pts_type != POINTS_OVERALL:
            m_objs = Mission.objects.filter(mnum=pts_type,is_boss=False)

        total_points = 0
        for m in m_objs:
            m_runs = Run.objects.filter(mission=m,is_obsolete=False)
            n_mission_runs = sum([1 for r in m_runs if r.has_video])
            runqset = all_user_runs.filter(mission=m,is_obsolete=False).order_by('time_s')

            if runqset.exists():
                total_points += n_mission_runs - (n_mission_runs - (runqset.first().get_rank() - 1))
            else:
                total_points += n_mission_runs
        return total_points

    def get_mission_ranks(self):
        qset = get_runner_haspoints()
        pdict = {}
        rank_overall = list(qset.order_by('points_overall').values_list('id', flat=True)).index(self.id) + 1
        pdict['Total'] = rank_overall
        for i in range(1,6,1):
            current_qset = qset.order_by(f'points_m{i}')
            rank_mission = list(current_qset.values_list('id',flat=True)).index(self.id) + 1
            pdict[f'M{i}'] = rank_mission
        current_qset = qset.order_by('points_boss')
        rank_mission = list(current_qset.values_list('id',flat=True)).index(self.id) + 1
        pdict['Boss'] = rank_mission
        return pdict






    def __str__(self):
        return f"TSC Name: {self.tsc_username} SRC Name: {self.src_username}"


class Mission(models.Model):
    id = models.IntegerField(primary_key=True)
    is_boss = models.BooleanField(default=False)
    level = models.CharField(max_length=4,choices=LEVEL_CHOICES+BOSS_CHOICES,default='GH')
    mnum = models.SmallIntegerField(default=1)

    def get_video_runs(self):
        all_runs = Run.objects.filter(mission=self,is_obsolete=False).order_by('time_s')
        vid_run_ids = [r.id for r in all_runs if r.has_video]
        vid_runs = Run.objects.filter(id__in=vid_run_ids)
        return vid_runs
    def num_runs(self):
        return self.get_video_runs().count()
    @property
    def world_record(self):
        wr = self.get_video_runs()
        if wr is not None:
            return wr.first()
        else:
            return Run.objects.filter(mission=self,is_obsolete=False).order_by('time_s').first()
    @property
    def level_slug(self):
        return self.get_level_display().lower().replace(" ", "_")

    def __str__(self):
        if not self.is_boss:
            return f"{self.get_level_display()} Mission {self.mnum}"
        return self.get_level_display()

class Run(models.Model):
    id = models.IntegerField(primary_key=True)
    runner = models.ForeignKey(Runner, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    time_s = models.DecimalField(decimal_places=2,max_digits=7)
    source = models.CharField(max_length=3, choices = TIME_SOURCE_CHOICES, default='TSC')
    comment = models.TextField(blank=True)
    date_performed = models.DateField()
    has_vid = models.BooleanField(default=False)
    is_obsolete = models.BooleanField(default=False)

    def time_tostr(self):
        mins = int(self.time_s) // 60
        secs = self.time_s - mins * 60
        return f"{mins:02}:{round(secs, 2):05}"

    @property
    def obsolete(self):
        run_qset = Run.objects.filter(runner=self.runner,time_s__lt=self.time_s,mission=self.mission)
        return run_qset.exists()

    @property
    def has_video(self):
        return len(URL_REGEX.findall(self.comment)) > 0 and 'http' in self.comment
    @property
    def video_link(self):
        if self.has_video:
            for match in URL_REGEX.findall(self.comment):
                if 'http' in match:
                    ext = match[-3:]
                    if ext.lower() not in IMG_EXT:
                        return match
                    return ""
    def get_rank(self):
        if self.has_video and not self.is_obsolete:
            runs = list(Run.objects.filter(mission=self.mission,is_obsolete=False).order_by('time_s'))

            run_times = [r.time_s for r in runs if r.has_video]
            ranks = rank_times_min(run_times)
            idx = run_times.index(self.time_s)
            return ranks[idx]
        return 0



    def __str__(self):
        return f"{self.mission} by {self.runner.username} in {self.time_tostr()} from {self.get_source_display().lower()} on {self.date_performed.strftime('%D')}"



