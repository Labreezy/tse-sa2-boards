import argparse
import time
from django.core.management.base import BaseCommand, CommandError
import srcomapi, srcomapi.datatypes as dtypes
import json
from datetime import date, datetime as dt
from boards.models import *

JSON_LOG_FMT = "src_runs_%m_%d_%y_%H_%M_%S_%p.json"
class Command(BaseCommand):
    help = "imports runs from SRC (levels only, no bosses)"

    def add_arguments(self, parser):
        parser.add_argument("--from-file", nargs=1, type=argparse.FileType('r'))

    def handle(self, *args, **options):
        print(options)
        if not options["from_file"]:
            sa2_game_id = 'l3dx0vdy'
            api = srcomapi.SpeedrunCom()
            api.debug = 1
            game = api.get_game(sa2_game_id)
            sa2runs = {}
            for level in game.levels:
                sa2runs[level.name] = []
                for category in filter(lambda c: c.type == 'per-level', game.categories):
                    print(f"{level.name} {category.name}")
                    mission_runs = []
                    lb = dtypes.Leaderboard(api, data=api.get(f"leaderboards/{sa2_game_id}/level/{level.id}/{category.id}?embed=runners"))
                    for r in lb.runs:
                        runobj = r['run']
                        uname = runobj.players[0].name
                        time_s = runobj.times['realtime_t']
                        if not runobj.comment:
                            comment = ""
                        else:
                            comment = runobj.comment
                        if len(runobj.videos.keys()) > 0:
                            vidlink = runobj.videos['links'][0]['uri']
                            comment += "\n\n" + vidlink
                        date_performed = runobj.date
                        mission_runs.append({"runner": uname, "time": time_s, "comment": comment, "date": date_performed})
                        time.sleep(.5)
                    sa2runs[level.name].append(mission_runs)
            json.dump(sa2runs, open(dt.now().strftime(JSON_LOG_FMT), 'w'), indent=2)
            self.stdout.write("Done with src API")
        else:
            print(options)
            sa2runs = json.load(options['from_file'][0])
        LEVEL_CHOICES_DICT = {long: short for short, long in LEVEL_CHOICES}
        for level in sa2runs.keys():
            curr_id = LEVEL_CHOICES_DICT[level]
            curr_level_runs = sa2runs[level]
            n_missions = 5
            if "green hill" in level.lower():
                n_missions = 1
            for i in range(n_missions):
                mission_obj = Mission.objects.filter(mnum=i+1,level=curr_id)
                if not mission_obj.exists():
                    mission_obj = Mission.objects.create(mnum=i+1,level=curr_id)
                else:
                    mission_obj = mission_obj.first()
                curr_mission_times = curr_level_runs[i]
                for run in curr_mission_times:
                    runner_name = run['runner']
                    src_qset = Runner.objects.filter(src_username=runner_name)
                    if not src_qset.exists():
                        r_obj = Runner.objects.create(src_username=runner_name,tsc_username=runner_name,tsc_as_primary=False)
                        #r_obj.save()
                    else:
                        r_obj = src_qset.first()
                for run in curr_mission_times:
                    runner_name = run['runner']
                    src_qset = Runner.objects.filter(src_username=runner_name)
                    r_obj = src_qset.first()
                    run_time = run['time']
                    run_comment = run['comment'].strip()
                    year, month, day = list(map(int, run['date'].split("-")))
                    run_date = date(year,month,day)
                    run_dupe_qset = Run.objects.filter(mission=mission_obj, time_s__gte=run_time, date_performed__lte=run_date, runner=r_obj)
                    if not run_dupe_qset.exists():
                        run_obj = Run.objects.create(runner=r_obj, mission=mission_obj, time_s=run_time, date_performed=run_date, comment=run_comment, source="SRC")
                    elif run_dupe_qset.first().source == 'TSC':
                        if run_dupe_qset.first().time_s == run_time:
                            print(f"Dupe found with comment {run_comment}")
                            tsc_run = run_dupe_qset.first()
                            tsc_run.comment = run_comment
                            tsc_run.time_s = run_time
                            tsc_run.date_performed = run_date
                            tsc_run.source = 'SRC'
                            tsc_run.save()
                            print(tsc_run)
                    elif run_dupe_qset.first().time_s > run_time:
                        tsc_run = run_dupe_qset.first()
                        print("Faster run found")
                        tsc_run.comment = run_comment
                        tsc_run.time_s = run_time
                        tsc_run.date_performed = run_date
                        tsc_run.source = 'SRC'
                        tsc_run.save()
                        print(tsc_run)
                    elif run_dupe_qset.first().date_performed < run_date:
                        print("Newer Run found")
                        tsc_run = run_dupe_qset.first()
                        tsc_run.comment = run_comment
                        tsc_run.time_s = run_time
                        tsc_run.date_performed = run_date
                        tsc_run.source = 'SRC'
                        tsc_run.save()
                        print(tsc_run)
            if n_missions == 1:
                break
        self.stdout.write("Done Importing")