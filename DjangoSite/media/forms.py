from .models import Book, Movie, Podcast, TVShow, Youtube
from django import forms


class TVForm(forms.ModelForm):
    class Meta:
        model = TVShow
        fields = "__all__"

    field_order = ["title, "]


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = "__all__"


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = "__all__"


class PodcastForm(forms.ModelForm):
    class Meta:
        model = Podcast
        fields = "__all__"


class YoutubeForm(forms.ModelForm):
    class Meta:
        model = Youtube
        fields = "__all__"
