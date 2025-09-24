from django import forms

from .models import Album, Comic, Movie, Novel, Podcast, TVShow, Youtube


class TVForm(forms.ModelForm):
    class Meta:
        model = TVShow
        fields = "__all__"


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


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = "__all__"
