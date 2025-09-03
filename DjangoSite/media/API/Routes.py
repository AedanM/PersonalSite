"""API Routes."""

from pathlib import Path
from typing import Any

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
    """Get Movie Data."""
    return dict(enumerate(await GetAllMovies()))  # pyright: ignore[reportGeneralTypeIssues]


@API_APP.get("/tvshows", summary="Full listing of tvshows")
async def TVShows() -> dict:
    """Get TV Data."""
    return dict(enumerate(await GetAllTV()))  # pyright: ignore[reportGeneralTypeIssues]


@API_APP.get("/genres", summary="Full listing of genre tags")
async def Genres() -> dict:
    """Get genres listing."""
    from media.modules.Utils import DEFINED_TAGS

    d = DEFINED_TAGS.copy()
    d.pop("Features")
    return d


@API_APP.get(path="/backup", summary="Full fat backup of DB")
async def Backup() -> dict:
    """Get full backup of DB."""
    return dict(await GetAll())  # pyright: ignore[reportGeneralTypeIssues]


class TagInfo(BaseModel):
    """Information struct for tags."""

    Title: str
    Year: int
    newTags: list


@API_APP.post(path="/addTags", summary="Append Tags to Tag List")
async def AppendTags(info: TagInfo) -> dict[str, Any]:
    """Append tags to media."""
    return dict(await AddTags(info.__dict__))  # pyright: ignore[reportGeneralTypeIssues]
