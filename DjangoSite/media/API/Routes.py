from pathlib import Path

from fastapi import FastAPI
from media.API.DBAccess import AddTags, GetAll, GetAllMovies, GetAllTV
from pydantic import BaseModel


description = (Path(__file__).parent / "Description.md").read_text()

API_APP = FastAPI(
    title="Media API",
    description=description,
    summary="Fast API access to media database",
    version="0.0.1",
    contact={
        "name": "Aedan McHale",
        "url": "https://aedanm.uk/resume",
        "email": "aedan.mchale@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


@API_APP.get("/movies", summary="Full listing of movies")
async def Movies() -> dict:
    return dict(enumerate(await GetAllMovies()))  # type: ignore


@API_APP.get("/tvshows", summary="Full listing of tvshows")
async def TVShows() -> dict:
    return dict(enumerate(await GetAllTV()))  # type: ignore


@API_APP.get("/genres", summary="Full listing of genre tags")
async def Genres() -> dict:
    from media.modules.Utils import DEFINED_TAGS

    d = DEFINED_TAGS.copy()
    d.pop("Features")
    return d


@API_APP.get(path="/backup", summary="Full fat backup of DB")
async def Backup() -> dict:
    return dict(await GetAll())  # type: ignore


class TagInfo(BaseModel):
    Title: str
    Year: int
    newTags: list


@API_APP.post(path="/addTags", summary="Append Tags to Tag List")
async def AppendTags(info: TagInfo):
    return dict(await AddTags(info.__dict__)) # type: ignore
