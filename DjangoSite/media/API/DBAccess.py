from asgiref.sync import sync_to_async

# pylint: disable = E1101
NON_API_FIELDS = ["Downloaded", "Logo"]


@sync_to_async
def GetAllMovies() -> list[dict]:
    from media.models import Movie

    movies = [x.JsonRepr for x in Movie.objects.all()]
    for m in movies:
        for field in NON_API_FIELDS:
            m.pop(field)
    return movies


@sync_to_async
def GetAllTV() -> list[dict]:
    from media.models import TVShow

    movies = [x.JsonRepr for x in TVShow.objects.all()]
    for m in movies:
        for field in NON_API_FIELDS:
            m.pop(field)
    return movies


@sync_to_async
def GetAll() -> dict:
    from media.modules.Utils import MODEL_LIST

    backupDict = {}
    for model in MODEL_LIST:
        # pylint: disable=E1101
        backupDict[model.__name__] = [x.JsonRepr for x in model.objects.all()]
    return backupDict
