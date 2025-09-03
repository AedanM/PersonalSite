"""Check the details of Media server vs website."""

import logging
import shutil
import time
from pathlib import Path
from typing import Any

import ffmpeg
import thefuzz.fuzz
from django.conf import settings as django_settings
from yaml import safe_load as load

from ..models import Movie, TVShow

STATIC_FILES = Path(django_settings.STATICFILES_DIRS[0]) / "Files"

LOGGER = logging.getLogger("UserLogger")


def CheckMovies() -> tuple[list, list]:
    movies = []
    with (django_settings.SYNC_PATH / "config" / "MediaServerSummary.yml").open(
        mode="r",
        encoding="ascii",
    ) as fp:
        movies = load(fp)["Movies"]

    ResetAlias(movies)
    unmatched, matched = FilterOutMatches(movies)

    return unmatched, matched


def FilterOutMatches(movies: list[dict], obj: Any = Movie) -> tuple[list, list]:
    movieList = obj.objects.all()
    matched = []
    unmatched = []
    rerender = []
    for m in movies:
        matches = (
            [
                x
                for x in movieList
                if MatchTitles(x.Title, m["Title"]) and abs(x.Year - int(m["Year"])) == 0
            ]
            if isinstance(m["Title"], str)
            else [x for x in movieList if x.id == m["Title"]]
        )
        if matches:
            m["Match"] = {
                "ID": matches[0].id,
                "Runtime": matches[0].Duration.seconds // 60,
                "Title": matches[0].Title,
                "Year": matches[0].Year,
                "Tag Diff": [x for x in m["Tags"] if x not in matches[0].GenreTagList],
                "Marked": matches[0].Downloaded,
                "Watched": matches[0].Watched,
            }
            m["Title"] = m["Match"]["Title"]
            matched.append(m)
            if matches[0].Duration.seconds // 60 / m["Size"] < 45:
                rerender.append(m["FilePath"])
            m = CleanAliasGroups(m)
        else:
            closest = sorted(
                movieList,
                key=lambda x, obj=m: thefuzz.fuzz.ratio(
                    str(obj["Title"]),
                    str(x.Title),
                ),
            )
            m["Closest"] = {"Title": closest[-1].Title, "Year": closest[-1].Year}
            unmatched.append(m)
    if rerender:
        Path(django_settings.SYNC_PATH / "config" / f"rerenderList{obj.__name__}.csv").write_text(
            data="\n".join(rerender),
            encoding="utf-8",
        )

    return unmatched, matched


def HandleReRenderQueue() -> None:
    renderList: list[str] = (
        Path(django_settings.SYNC_PATH / "config" / "rerenderList.csv")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    start = time.time()
    renderOutput: list[str] = []
    if not renderList:
        raise FileNotFoundError
    for file in renderList:
        f = Path(file.replace("\n", ""))
        try:
            if not f.exists():
                raise FileNotFoundError(f)
            stream = ffmpeg.probe(f)
            stream = stream["streams"][0]
            renderOutput.append(f"{f},{stream['width']},{stream['height']}")
        except ffmpeg.Error as e:
            LOGGER.error(e.stderr)
            renderOutput.append(file)
    Path(django_settings.SYNC_PATH / "config" / "rerenderList.csv").write_text(
        data="\n".join(renderOutput),
        encoding="utf-8",
    )
    LOGGER.info("Render Log Written in %f", time.time() - start)


def CopyOverRenderQueue() -> None:
    renderList: list[str] = (
        Path(django_settings.SYNC_PATH / "config" / "rerenderList.csv")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    for file in renderList:
        f = Path(file.replace("\n", "").split(",")[0])
        w = int(file.replace("\n", "").split(",")[1])
        h = int(file.replace("\n", "").split(",")[2])
        parentDir: Path = Path(r"H:\DownloadBuffer\RenderQueue")
        subFolder: str = "SD" if w * h <= (1280 * 720) else "4k" if w * h > (1920 * 1080) else "HD"
        dst: Path = parentDir / subFolder / f.name
        if not f.exists():
            raise FileNotFoundError(f)
        if not dst.exists():
            shutil.copy(f, dst)
        LOGGER.info("%s Copied to %s", f.name, subFolder)


def MatchTitles(t1: str, t2: str) -> bool:
    badChars = [".", ",", ":", "!", "'", "?", '"', "-", " ", "The ", "A "]
    t1 = t1.replace("&", "and")
    t2 = t2.replace("&", "and")
    for char in badChars:
        t1 = t1.replace(char, "")
        t2 = t2.replace(char, "")
    return t1.lower() == t2.lower()


def CleanAliasGroups(obj: dict) -> dict:
    ymlFile = load(Path(django_settings.SYNC_PATH / "config" / "Alias.yml").read_text())
    groups = ymlFile["Pools"]
    for diff in obj["Match"]["Tag Diff"]:
        for g in [x for x in groups if diff in x]:
            if any(x for x in g if x in obj["Tags"]):
                obj["Match"]["Tag Diff"].remove(diff)
                break
    return obj


def ResetAlias(files: dict | list[dict]) -> None:
    ymlFile = load(Path(django_settings.SYNC_PATH / "config" / "Alias.yml").read_text())
    titles = ymlFile["Titles"]
    tags = ymlFile["Tags"]
    if isinstance(files, dict):
        files = list(files.values())

    for f in files:
        if f["Title"] in titles:
            f["Title"] = titles[f["Title"]]
        fileTags = []
        for tag in f["Tags"]:
            if tag in tags:
                fileTags.append(tags[tag])
            else:
                fileTags.append(tag)
        f["Tags"] = fileTags


def CheckTV() -> tuple[list, list]:
    shows = load(Path(django_settings.SYNC_PATH / "config" / "MediaServerSummary.yml").read_text())[
        "TV Shows"
    ]

    ResetAlias(shows)
    unmatched, matched = FilterOutTVMatches(shows)

    return unmatched, matched


def FilterOutTVMatches(files: list) -> tuple[list, list]:
    tvList = TVShow.objects.all()
    matched = []
    unmatched = []
    rerender = []
    for m in files:
        matches = (
            [x for x in tvList if MatchTitles(x.Title, m["Title"])]
            if isinstance(m["Title"], str)
            else [x for x in tvList if x.id == m["Title"]]  # pyright: ignore[reportAttributeAccessIssue]
        )
        if matches:
            m["Match"] = {
                "ID": matches[0].id,  # # pyright: ignore[reportAttributeAccessIssue]
                "Runtime": (matches[0].Duration.seconds // 60) * m["Count"],
                "Year": matches[0].Year,
                "Tag Diff": [x for x in m["Tags"] if x not in matches[0].GenreTagList],
                "Marked": matches[0].Downloaded,
                "Count": matches[0].Length,
                "Watched": matches[0].Watched,
            }
            m["Title"] = matches[0].Title
            m["CountDiff"] = matches[0].Length - m["Count"]
            matched.append(m)
            if m["Match"]["Runtime"] / m["Size"] < 45:
                rerender.append(m["FilePath"])
            m = CleanAliasGroups(m)
        else:
            closest = sorted(
                tvList,
                key=lambda x, obj=m: thefuzz.fuzz.ratio(str(obj["Title"]), str(x.Title)),
            )
            m["Closest"] = {"Title": closest[-1].Title, "Year": closest[-1].Year}
            unmatched.append(m)
    if rerender:
        Path(django_settings.SYNC_PATH / "config" / "rerenderListTV.csv").write_text(
            "\n".join(rerender),
        )
    return unmatched, matched
