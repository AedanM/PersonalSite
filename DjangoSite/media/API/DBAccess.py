from asgiref.sync import sync_to_async

NON_API_FIELDS = ["Downloaded", "Logo"]


@sync_to_async
def GetAllMovies():
    from media.models import Movie

    movies = [x.JsonRepr for x in Movie.objects.all()]
    for m in movies:
        for field in NON_API_FIELDS:
            m.pop(field)
    return movies


@sync_to_async
def GetAllTV():
    from media.models import TVShow

    movies = [x.JsonRepr for x in TVShow.objects.all()]
    for m in movies:
        for field in NON_API_FIELDS:
            m.pop(field)
    return movies
