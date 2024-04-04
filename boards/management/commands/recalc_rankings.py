from django.core.management import BaseCommand

from boards.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        for runner in Runner.objects.all():
            runner.recalculate_allpoints()
            self.stdout.write(f"{runner.username}: {runner.points_overall} overall")
            runner.save()
        print("Done!")