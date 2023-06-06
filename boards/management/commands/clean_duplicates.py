from django.core.management import BaseCommand

from boards.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        for run in Run.objects.all():
            dupes = Run.objects.filter(runner=run.runner,mission=run.mission,time_s__gte=run.time_s,date_performed__lte=run.date_performed).order_by('date_performed','time_s')
            if dupes.count() > 1:
                print(f'Found {dupes.count()} duplicates')
                for d in dupes:
                    print(f"{d} on {d.date_performed}")
                dupes.first().delete()

