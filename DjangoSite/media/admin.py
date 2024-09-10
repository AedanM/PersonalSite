# pylint: disable=C0103
from django.contrib import admin

from .models import Album, Comic, Movie, Novel, Podcast, TVShow, Youtube


class MediaAdmin(admin.ModelAdmin):
    empty_value_display = "-Not Set-"


admin.site.register(Album, MediaAdmin)
admin.site.register(Comic, MediaAdmin)
admin.site.register(Movie, MediaAdmin)
admin.site.register(Novel, MediaAdmin)
admin.site.register(Podcast, MediaAdmin)
admin.site.register(TVShow, MediaAdmin)
admin.site.register(Youtube, MediaAdmin)
# Register your models here.
