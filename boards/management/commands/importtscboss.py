import requests, bs4
import json
from django.core.management import BaseCommand

from boards.models import *
from datetime import date, datetime as dt

def str_to_sec(s):
    nums = s.split(":")
    if len(nums) == 3:
        return 60*int(nums[0]) + int(nums[1]) + float(nums[2])/100.0
    return -1
JSON_LOG_FMT = "tsc_runs_%m_%d_%y_%H_%M_%S_%p.json"

class Command(BaseCommand):

    help = "Imports bosses from TSC"
    def handle(self, *args, **options):
        tsc_sa2b_page = "https://www.soniccenter.org/rankings/sonic_adventure_2_b/bosses"
        tsc_domain = "https://www.soniccenter.org"
        sa2br = requests.get(tsc_sa2b_page)
        sa2rankingstr = sa2br.text
        runs_dict = {}
        css_soup = bs4.BeautifulSoup(sa2rankingstr)
        a = css_soup.select(".innerdata tr td a")[13:82]
        stages = []
        mission_urls = []

        for a_el in filter(lambda el: "members" not in el["href"] and "overall" not in el["href"], a):
            stage_name = a_el['href'].split("/")[-2]
            if stage_name == "bosses":
                continue
            stage_name = " ".join(map(lambda s: s.capitalize(), stage_name.split("_")))
            if stage_name not in stages and stage_name != "Times":
                if stage_name == "Egg Golem":
                    is_dark = any(["Golem" in s for s in stages])
                    if not is_dark:
                        stage_name += " (Hero)"

                    else:
                        print("dark found")
                        stage_name += " (Dark)"
                        stages.append(stage_name)
                        mission_urls.append(tsc_domain + a_el['href'] + '/dark')
                        continue
                stages.append(stage_name)
                mission_urls.append(tsc_domain + a_el['href'])





        for idx, murl in enumerate(mission_urls):

            gen_murl = "/".join(murl.split("/")[:-1])
            mission_rankings = []
            resp = requests.get(gen_murl)
            print(gen_murl)
            print(resp.status_code)
            if resp.status_code == 404:
                continue
            soup = bs4.BeautifulSoup(resp.text)
            trs = soup.select('.innerdata tr')
            for row in trs[1:-1]:
                run = {}
                row_cells =  row.find_all("td")
                run['place'] = int(row_cells[0].text)
                run['runner'] = row_cells[1].text
                run['time'] = str_to_sec(row_cells[2].text)
                if row_cells[2].get("title"):
                    run['comment'] = row_cells[2].get("title")
                run['date'] = row_cells[3].text
                mission_rankings.append(run)
            stg_name = stages[idx]
            if stg_name not in runs_dict.keys():
                runs_dict[stg_name] = []
            runs_dict[stg_name].append(mission_rankings)

        json.dump(runs_dict, open(dt.now().strftime(JSON_LOG_FMT), "w"),indent=2)
        for mission in Mission.objects.all():
            sources = Run.objects.filter(mission=mission).values('source').distinct()
            if sources.count() == 1 and sources.first()['source'] == 'SRC':
                print(mission)
                level_name = mission.get_level_display()
                m_idx = mission.mnum-1
                if 'route' in level_name.lower() and mission.mnum >= 3:
                    continue
                if 'green hill' in level_name.lower() and mission.mnum > 1:
                    continue
                runs_list = runs_dict[level_name][m_idx]
                for r_dict in runs_list:
                    runner_qset = Runner.objects.filter(tsc_username=r_dict['runner'])
                    if runner_qset.exists():
                        runner_obj = runner_qset.first()
                    else:
                        runner_obj = Runner.objects.create(tsc_username=r_dict['runner'],src_username=r_dict['runner'],tsc_as_primary=True)
                for r_dict in runs_list:
                    runner_obj = Runner.objects.filter(tsc_username=r_dict['runner']).first()
                    time_s = r_dict['time']
                    m, d, y = list(map(int, r_dict['date'].split("-")))
                    y += 2000
                    date_p = date(y,m,d)
                    comment = r_dict.get("comment","")
                    runs_qset = Run.objects.filter(mission=mission,is_boss=True,time_s__gte=time_s,runner=runner_obj)
                    if not runs_qset.exists():
                        Run.objects.create(mission=mission,is_boss=True,time_s=time_s,runner=runner_obj,comment=comment,date_performed=date_p)
                    elif runs_qset.first().time_s > time_s:
                        r = runs_qset.first()
                        r.time_s = time_s
                        r.comment = comment
                        r.date_performed=date_p
                        r.save()
                        print(f"{r.mission.get_level_display()} M{r.mission.mnum} by {runner_obj.username} in {time_s} saved")