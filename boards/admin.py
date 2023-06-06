from django.contrib import admin
from boards.models import *
# Register your models here.
@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('runner', 'mission', 'time_s', 'source')
    list_filter = ('mission',)
@admin.register(Runner)
class RunnerAdmin(admin.ModelAdmin):
    list_display = ('tsc_username', 'src_username', 'tsc_as_primary')
    search_fields = ['tsc_username','src_username']

admin.site.register(Mission)
