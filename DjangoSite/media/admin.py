from django.contrib import admin

from .models import Book, Movie, Podcast, TVShow, Youtube

admin.site.register(TVShow)
admin.site.register(Movie)
admin.site.register(Youtube)
admin.site.register(Book)
admin.site.register(Podcast)

# Register your models here.
