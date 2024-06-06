# pylint: disable=C0103
from django.contrib import admin

from .models import Comic, Movie, Novel, Podcast, TVShow, Youtube


class MediaAdmin(admin.ModelAdmin):
    empty_value_display = "-Not Set-"


admin.site.register(TVShow, MediaAdmin)
admin.site.register(Movie, MediaAdmin)
admin.site.register(Youtube, MediaAdmin)
admin.site.register(Comic, MediaAdmin)
admin.site.register(Novel, MediaAdmin)
admin.site.register(Podcast, MediaAdmin)

# Register your models here.
