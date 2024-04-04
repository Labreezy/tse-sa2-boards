import argparse
import time
from django.core.management.base import BaseCommand, CommandError
import srcomapi, srcomapi.datatypes as dtypes
import json
import requests
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

            sa2runs = {}
            qparams_level = {"order": "pos"}
            resp = requests.get("https://speedrun.com/api/v1/games/" + sa2_game_id + "/levels", params=qparams_level)

            level_dict = resp.json()
            skip = True
            for level in level_dict['data']:
                levelname = level['name']
                if skip:
                    skip = levelname != "Big Foot"
                    if skip:
                        continue
                self.stdout.write(levelname)
                sa2runs[levelname] = []
                cat_resp = requests.get(f"https://speedrun.com/api/v1/levels/{level['id']}/categories")
                if cat_resp.status_code != 200:
                    print(f"Status code {cat_resp.status_code} encountered")
                    print(json.dumps(cat_resp.json(), indent=2))
                    return
                cat_json = cat_resp.json()
                if len(cat_json['data']) < 5:
                    cat_ids = [cat['id'] for cat in cat_json['data']]
                else:
                    cat_ids = [cat['id'] for cat in cat_json['data'][:5]]
                for cat_id in cat_ids:
                    mission_runs = []
                    has_next = True
                    params = {

                        'level': level['id'],
                        'embed': "players",
                        "status": "verified",
                        "category": cat_id,
                        "order_by": "date",
                        "direction": "desc"

                    }

                    runs_resp = requests.get(f"https://speedrun.com/api/v1/runs", params=params)

                    while has_next:
                        if runs_resp.status_code == 200:
                            data = runs_resp.json()['data']

                            for run in data:
                                player_json = run['players']['data'][0]
                                if player_json['rel'] != "user":
                                    username = player_json['name']
                                else:
                                    username = player_json['names']['international']
                                time_s = run['times']['primary_t']
                                if run['comment'] is None:
                                    comment = ""
                                else:
                                    comment = run['comment']
                                if len(run['videos']['links']) > 0:
                                    vid_link = run['videos']['links'][0]['uri']
                                    comment += "\n\n" + vid_link
                                run_date = run['date']
                                mission_runs.append(
                                    {"runner": username, "time": time_s, "comment": comment, "date": run_date})
                            pages = runs_resp.json()['pagination']['links']
                            has_next = False
                            for p in pages:
                                if p['rel'] == 'next':
                                    has_next = True
                            if has_next:
                                time.sleep(.25)
                                runs_resp = requests.get(p['uri'])
                        else:
                            print(f"Status code: {runs_resp.status_code}")
                            return
                    sa2runs[levelname].append(mission_runs)
                    time.sleep(.25)
            json.dump(sa2runs, open(dt.now().strftime(JSON_LOG_FMT), 'w'), indent=2)
            self.stdout.write("Done with src API")

        else:
            print(options)
            sa2runs = json.load(options['from_file'][0])
        LEVEL_CHOICES_DICT = {long: short for short, long in LEVEL_CHOICES + BOSS_CHOICES}
        BOSS_LIST = [bc[1] for bc in BOSS_CHOICES]
        for level in sa2runs.keys():
            curr_id = LEVEL_CHOICES_DICT[level]
            curr_level_runs = sa2runs[level]
            n_missions = 5
            is_boss = False
            if "green hill" in level.lower() or level in BOSS_LIST:
                n_missions = 1
                if level in BOSS_LIST:
                    is_boss = True
            for i in range(n_missions):
                mission_obj = Mission.objects.filter(mnum=i+1,level=curr_id, is_boss=is_boss)
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

        self.stdout.write("Done Importing, cleaning up duplicates/obsoletes")
        for run in Run.objects.all():
            dupes = Run.objects.filter(runner=run.runner,mission=run.mission,time_s__gte=run.time_s,date_performed__lte=run.date_performed).order_by('date_performed','time_s')
            if dupes.count() > 1:
                print(f'Found {dupes.count()} duplicates')
                for d in dupes:
                    print(f"{d} on {d.date_performed}")
                dupes.first().delete()
        self.stdout.write("Done cleaning, recalculating points")
        for runner in Runner.objects.all():
            runner.recalculate_allpoints()
            self.stdout.write(f"{runner.username}: {runner.points_overall} overall")
            runner.save()
        print("Done!")
