import logging

from asgiref.sync import sync_to_async
from fastapi import HTTPException

# pylint: disable = E1101
NON_API_FIELDS = ["Downloaded", "Logo"]


LOGGER = logging.getLogger("UserLogger")


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


@sync_to_async
def AddTags(lookupData: dict):
    from media.modules.Utils import MODEL_LIST

    matchObj = None
    for model in MODEL_LIST:
        matching = [x for x in model.objects.all() if x.Title == lookupData["Title"]]
        if len(matching) == 1:
            matchObj = matching[0]
            break
        elif len(matching) == 0:
            break
        if "Year" in dir(matching[0]):
            matching = [x for x in matching if x.Year == lookupData["Year"]]
        if len(matching) == 1:
            matchObj = matching[0]
            break
    if matchObj is not None:
        matchObj.Genre_Tags = ",".join(
            sorted(list(set(matchObj.Genre_Tags.split(",") + lookupData["newTags"])))
        )
        matchObj.save()
        LOGGER.info(
            "%s (%d) added %d tags -> %s",
            matchObj.Title,
            matchObj.id,
            len(lookupData["newTags"]),
            ",".join(lookupData["newTags"]),
        )
        return {"id": matchObj.id, "tags": matchObj.Genre_Tags, "Title": matchObj.Title}
    raise HTTPException(status_code=404, detail="Item not found")
