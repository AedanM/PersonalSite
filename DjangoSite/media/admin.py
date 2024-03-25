from django.contrib import admin

from .models import Movie, TVShow

admin.site.register(TVShow)
admin.site.register(Movie)
# Register your models here.
