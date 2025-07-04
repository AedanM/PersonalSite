import json
import logging
import shutil
import time
from pathlib import Path
from typing import Any

import ffmpeg  # type: ignore
import thefuzz.fuzz
from django.conf import settings as django_settings

from ..models import Movie, TVShow

STATIC_FILES = Path(django_settings.STATICFILES_DIRS[0]) / "Files"

LOGGER = logging.getLogger("UserLogger")


def CheckMovies():
    movies = []
    with (django_settings.SYNC_PATH / "config" / "MediaServerSummary.json").open(
        mode="r", encoding="ascii"
    ) as fp:
        movies = json.load(fp)["Movies"]

    ResetAlias(movies)
    unmatched, matched = FilterOutMatches(movies)

    return unmatched, matched


def FilterOutMatches(movies, obj: Any = Movie):
    # pylint: disable=E1101
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
            else [x for x in movieList if x.id == m["Title"]]  # type: ignore
        )
        if matches:
            m["Match"] = {
                "ID": matches[0].id,  # type:ignore
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
                key=lambda x, obj=m: thefuzz.fuzz.ratio(  # type:ignore
                    str(obj["Title"]), str(x.Title)
                ),
            )
            m["Closest"] = {"Title": closest[-1].Title, "Year": closest[-1].Year}
            unmatched.append(m)
    if rerender:
        with open(
            file=django_settings.SYNC_PATH / "config" / f"rerenderList{obj.__name__}.csv",
            mode="w",
            encoding="ascii",
        ) as fp:
            fp.write("\n".join(rerender))

    return unmatched, matched


def HandleReRenderQueue():
    renderList = []
    with open(
        file=django_settings.SYNC_PATH / "config" / "rerenderList.csv", mode="r", encoding="ascii"
    ) as fp:
        renderList = fp.readlines()
    start = time.time()
    renderOutput = []
    if not renderList:
        raise FileNotFoundError
    # pylint:disable=E1101
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
    with open(
        file=django_settings.SYNC_PATH / "config" / "rerenderList.csv", mode="w", encoding="ascii"
    ) as fp:
        fp.write("\n".join(renderOutput))
    LOGGER.info("Render Log Written in %f", time.time() - start)


def CopyOverRenderQueue():
    renderList = []
    with open(
        file=django_settings.SYNC_PATH / "config" / "rerenderList.csv",
        mode="r",
        encoding="ascii",
    ) as fp:
        renderList = fp.readlines()
    for file in renderList:
        f = Path(file.replace("\n", "").split(",")[0])
        w = int(file.replace("\n", "").split(",")[1])
        h = int(file.replace("\n", "").split(",")[2])
        parentDir = Path(r"H:\DownloadBuffer\RenderQueue")
        subFolder = "SD" if w * h <= (1280 * 720) else "4k" if w * h > (1920 * 1080) else "HD"
        dst = parentDir / subFolder / f.name
        if not f.exists():
            raise FileNotFoundError(f)
        if not dst.exists():
            shutil.copy(f, dst)
        LOGGER.info("%s Copied to %s", f.name, subFolder)


def MatchTitles(t1, t2) -> bool:
    # return thefuzz.fuzz.ratio(t1.lower(), t2.lower()) > 93
    badChars = [".", ",", ":", "!", "'", "?", '"', "-", " ", "The ", "A "]
    t1 = t1.replace("&", "and")
    t2 = t2.replace("&", "and")
    for char in badChars:
        t1 = t1.replace(char, "")
        t2 = t2.replace(char, "")
    return t1.lower() == t2.lower()


def CleanAliasGroups(obj: dict) -> dict:
    with (django_settings.SYNC_PATH / "config" / "Alias.json").open(
        mode="r", encoding="ascii"
    ) as fp:
        jsonFile = json.load(fp)
        groups = jsonFile["Pools"]
    for diff in obj["Match"]["Tag Diff"]:
        for g in [x for x in groups if diff in x]:
            # [a,b,c]
            if any(x for x in g if x in obj["Tags"]):
                obj["Match"]["Tag Diff"].remove(diff)
                break
    return obj


def ResetAlias(files):
    titles = {}
    tags = {}
    with (django_settings.SYNC_PATH / "config" / "Alias.json").open(
        mode="r", encoding="ascii"
    ) as fp:
        jsonFile = json.load(fp)
        titles = jsonFile["Titles"]
        tags = jsonFile["Tags"]
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


def CheckTV():
    shows = []
    with (django_settings.SYNC_PATH / "config" / "MediaServerSummary.json").open(
        mode="r", encoding="ascii"
    ) as fp:
        shows = json.load(fp)["TV Shows"]

    ResetAlias(shows)
    unmatched, matched = FilterOutTVMatches(shows)

    return unmatched, matched


def FilterOutTVMatches(files: list):
    # pylint: disable=E1101
    tvList = TVShow.objects.all()
    matched = []
    unmatched = []
    rerender = []
    for m in files:
        matches = (
            [x for x in tvList if MatchTitles(x.Title, m["Title"])]
            if isinstance(m["Title"], str)
            else [x for x in tvList if x.id == m["Title"]]  # type: ignore
        )
        if matches:
            m["Match"] = {
                "ID": matches[0].id,  # type:ignore
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
                key=lambda x, obj=m: thefuzz.fuzz.ratio(
                    str(obj["Title"]), str(x.Title)
                ),  # type:ignore
            )
            m["Closest"] = {"Title": closest[-1].Title, "Year": closest[-1].Year}
            unmatched.append(m)
    if rerender:
        with open(
            file=django_settings.SYNC_PATH / "config" / "rerenderListTV.csv",
            mode="w",
            encoding="ascii",
        ) as fp:
            fp.write("\n".join(rerender))

    return unmatched, matched
