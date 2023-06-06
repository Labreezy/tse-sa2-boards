from django.core.management import BaseCommand
from boards.models import *


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('src_name', type=str)
        parser.add_argument('tsc_name', nargs='?', type=str)

    def handle(self, *args, **options):
        tsc_name = options.get('tsc_name',"")
        src_name = options['src_name']
        if tsc_name != "":
            potential_dupes_1 = Runner.objects.filter(tsc_username__iexact=tsc_name,src_username__iexact=src_name)
        else:
            potential_dupes_1 = Runner.objects.filter(tsc_username__iexact=src_name,src_username__iexact=src_name)
        if potential_dupes_1.exists():

            runner_pks = [r.id for r in potential_dupes_1]
            #create a new runner object with the tsc and src usernames
            if tsc_name != "":
                merge_runner, merge_exists = Runner.objects.get_or_create(tsc_username=tsc_name,src_username=src_name)
                if merge_exists:
                    Run.objects.filter(runner=merge_runner).delete()
                all_duplicate_runs = Run.objects.filter(runner__id__in=runner_pks).order_by('mission')
                for run in all_duplicate_runs:

                    obsoletes = all_duplicate_runs.filter(time_s__lt=run.time_s,mission=run.mission)
                    if obsoletes.exists():
                        print(str(obsoletes.first()) + " obsoletes " + str(run))
                        run.delete()
                        obsoletes.first().runner = merge_runner

                    duplicates = all_duplicate_runs.filter(time_s=run.time_s,mission=run.mission)
                    if duplicates.exists():
                        for d in duplicates:
                            if d.id != run.id:
                                print(f"{d} is a duplicate of the run {run}")
                                if d.source == 'SRC':
                                    d.runner = merge_runner
                                    d.runner.save()
                                    d.save()
                                    run.delete()
                                else:
                                    run.runner = merge_runner
                                    run.runner.save()
                                    run.save()
                                    d.delete()





