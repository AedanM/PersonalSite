from .models import Comic, Novel, Movie, Podcast, TVShow, Youtube
from django import forms


class TVForm(forms.ModelForm):
    class Meta:
        model = TVShow
        fields = "__all__"

    field_order = ["title, "]


class ComicForm(forms.ModelForm):
    class Meta:
        model = Comic
        fields = "__all__"


class NovelForm(forms.ModelForm):
    class Meta:
        model = Novel
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
