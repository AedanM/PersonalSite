import json
import logging
import os
import shutil
import time
from pathlib import Path

import cv2
import ffmpeg
import thefuzz.fuzz

try:
    from django.conf import settings as django_settings

    from ..models import Movie, TVShow

    STATIC_FILES = Path(django_settings.STATICFILES_DIRS[0]) / "Files"

    LOGGER = logging.getLogger("UserLogger")
except:
    pass


def CheckMovies():
    movies = []
    with (STATIC_FILES / "MediaServerSummary.json").open(mode="r", encoding="ascii") as fp:
        movies = json.load(fp)["Movies"]

    ResetAlias(movies)
    unmatched, matched = FilterOutMatches(movies)

    return unmatched, matched


def FilterOutMatches(movies):
    movieList = Movie.objects.all()
    matched = []
    unmatched = []
    rerender = []
    for m in movies:
        matches = [
            x
            for x in movieList
            if MatchTitles(x.Title, m["Title"]) and abs(x.Year - int(m["Year"])) == 0
        ]
        if matches:
            m["Match"] = {
                "ID": matches[0].id,  # type:ignore
                "Runtime": matches[0].Duration.seconds // 60,
                "Title": matches[0].Title,
                "Year": matches[0].Year,
                "Tag Diff": [
                    x for x in m["Tags"] if ResetAliasTags(x) not in matches[0].GenreTagList
                ],
                "Marked": matches[0].Downloaded,
            }
            matched.append(m)
            if matches[0].Duration.seconds // 60 / m["Size"] < 45:
                rerender.append(m["FilePath"])
        else:
            closest = sorted(movieList, key=lambda x: thefuzz.fuzz.ratio(m["Title"], x.Title))
            m["Closest"] = {"Title": closest[-1].Title, "Year": closest[-1].Year}
            unmatched.append(m)
    if rerender:
        with open(file=Path("./static/files/rerenderList.csv"), mode="w", encoding="ascii") as fp:
            fp.write("\n".join(rerender))

    return unmatched, matched


def HandleReRenderQueue():
    renderList = []
    with open(file=Path("./static/files/rerenderList.csv"), mode="r", encoding="ascii") as fp:
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
    with open(file=Path("./static/files/rerenderList.csv"), mode="w", encoding="ascii") as fp:
        fp.write("\n".join(renderOutput))
    LOGGER.info("Render Log Written in %f", time.time() - start)


def CopyOverRenderQueue():
    renderList = []
    with open(file=Path("./static/files/rerenderList.csv"), mode="r", encoding="ascii") as fp:
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
    badChars = [".", ",", ":", "!", "'", '"', "-", " "]
    t1 = t1.replace("&", "and")
    t2 = t2.replace("&", "and")
    for char in badChars:
        t1 = t1.replace(char, "")
        t2 = t2.replace(char, "")
    return t1.lower() == t2.lower()


def ResetAliasTags(string):

    return string


def ResetAlias(files):
    titles = {}
    tags = {}
    with (STATIC_FILES / "Alias.json").open(mode="r", encoding="ascii") as fp:
        jsonFile = json.load(fp)
        titles = jsonFile["Titles"]
        tags = jsonFile["Tags"]
    for file in files:
        if file["Title"] in titles:
            file["Title"] = titles[file["Title"]]
        fileStr = ",".join(file["Tags"])
        for tag in file["Tags"]:
            if tag in tags:
                fileStr = fileStr.replace(tag, tags[tag])
        file["Tags"] = fileStr.split(",")
