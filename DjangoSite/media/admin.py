from django.contrib import admin

from .models import Comic, Novel, Movie, Podcast, TVShow, Youtube

admin.site.register(TVShow)
admin.site.register(Movie)
admin.site.register(Youtube)
admin.site.register(Comic)
admin.site.register(Novel)
admin.site.register(Podcast)

# Register your models here.
