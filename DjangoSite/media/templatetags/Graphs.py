import datetime
import hashlib
import json
import logging
import shutil
from functools import wraps
from math import ceil
from pathlib import Path
from time import time

import pandas as pd
import plotly.express as px  # type:ignore
import statsmodels.api as sm  # type:ignore
from django import template
from django.conf import settings as django_settings

from ..utils import MINIMUM_YEAR

DEFINED_TAGS = {}
with open(django_settings.SYNC_PATH / "Genres.json", encoding="ascii") as fp:
    DEFINED_TAGS = json.load(fp)
    DEFINED_TAGS.pop("_comment", None)

register = template.Library()

LOGGER = logging.getLogger("UserLogger")

WATCH_COLOR_MAP = {
    "Watched": "blue",
    "Downloaded": "lightgreen",
    "Neither": "red",
    "Watched On MS": "#1111FF",
    "Watched Streaming": "purple",
}


def DatabaseMD5():
    hashMD5 = hashlib.md5()
    path = Path(django_settings.DATABASES["default"]["NAME"])
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashMD5.update(chunk)
    return hashMD5.hexdigest()


def GetDst(objList, plotName):
    mediaType = objList[0].__class__.__name__
    dstFolder = Path(django_settings.STATICFILES_DIRS[0]) / f"stats/{DatabaseMD5()}"
    if not dstFolder.exists():
        for f in dstFolder.parent.glob("**/*/"):
            shutil.rmtree(f)
        dstFolder.mkdir()
    dstFile = dstFolder / f"{plotName}-{mediaType}.html"
    return dstFile


def LogTiming(f):
    @wraps(f)
    def Wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        LOGGER.debug("func:%r took: %2.4f sec", f.__name__, te - ts)
        return result

    return Wrap


@register.filter
def RatingOverTime(objList: list, force: bool) -> str:
    outputDiv = ""
    df = None
    dstPath = GetDst(objList, "RatingVsTime")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        if getattr(objList[0], "Year", None):
            df = pd.DataFrame(
                {
                    "Title": [x.Title for x in objList if x.Watched],
                    "Release Year": [x.Year for x in objList if x.Watched],
                    "Rating": [x.Rating for x in objList if x.Watched],
                    "Duration": [x.Duration.seconds // 60 for x in objList if x.Watched],
                }
            )
        elif getattr(objList[0], "Series_Start", None):
            df = pd.DataFrame(
                {
                    "Title": [x.Title for x in objList if x.Watched],
                    "Release Year": [x.Series_Start.year for x in objList if x.Watched],
                    "Rating": [x.Rating for x in objList if x.Watched],
                }
            )
        if df is not None:
            fig = px.scatter(
                df,
                x="Release Year",
                y="Rating",
                title="Rating Over Time",
                hover_name="Title",
                color="Duration",
                color_continuous_scale="Electric",
            )
            rollingTrend = sm.nonparametric.lowess(df["Rating"], df["Release Year"], frac=0.35)

            fig.add_scatter(
                x=rollingTrend[:, 0],
                y=rollingTrend[:, 1],
                mode="lines",
            )
            fig.update_layout(showlegend=False)

            outputDiv = GetHTML(fig)
            dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.filter
def DurationOverTime(objList: list, force: bool) -> str:
    outputDiv = ""
    df = None
    dstPath = GetDst(objList, "DurationVsTime")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        useTotal = getattr(objList[0], "Total_Length", None) is not None
        df = pd.DataFrame(
            {
                "Title": [x.Title for x in objList],
                "Year": [x.Year for x in objList],
                "Duration": [
                    x.Duration.seconds / 60 if not useTotal else x.Total_Length for x in objList
                ],
                "Watched": [
                    "Watched" if x.Watched else "Downloaded" if x.Downloaded else "Neither"
                    for x in objList
                ],
            }
        )
        if df is not None:
            fig = px.scatter(
                df,
                x="Year",
                y="Duration",
                color="Watched",
                color_discrete_map=WATCH_COLOR_MAP,
                labels={"x": "Release Year", "y": "Duration (minutes)"},
                title="Duration Over Time",
                hover_name="Title",
                log_y=useTotal,
            )
            rollingTrend = sm.nonparametric.lowess(df["Duration"], df["Year"], frac=0.2)

            fig.add_scatter(
                x=rollingTrend[:, 0],
                y=rollingTrend[:, 1],
                mode="lines",
                name="Average",
            )
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.2,
                    xanchor="center",
                    x=0.5,
                )
            )
            outputDiv = GetHTML(fig)
            dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.filter
def DecadeBreakdown(objList: list, force: bool) -> str:
    outputDiv = ""
    labels = []
    values = []
    dstPath = GetDst(objList, "DecadeBreakdown")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        if getattr(objList[0], "Year", None):
            startDecade = (min(x.Year for x in objList) // 10) * 10
            for year in range(startDecade, 2030, 10):
                labels.append(f"{year}s")
                values.append(len([x for x in objList if x.Year >= year and x.Year < year + 10]))
        elif getattr(objList[0], "Series_Start", None):
            startDecade = (min(x.Series_Start for x in objList).year // 10) * 10
            for year in range(startDecade, 2030, 10):
                labels.append(f"{year}s")
                values.append(len([x for x in objList if year <= x.Series_Start.year < year + 10]))
        if labels and values:
            fig = px.pie(
                category_orders={"names": labels},
                hole=0.25,
                names=labels,
                title="Release Decade by Year",
                values=values,
            )
            outputDiv = GetHTML(fig, True)
            dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.filter
def RuntimeBreakdown(objList: list, force: bool) -> str:
    outputDiv = ""
    labels = []
    values = []
    dstPath = GetDst(objList, "RuntimeBreakdown")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        if getattr(objList[0], "Series_Start", None):
            startDecade = (min(x.Series_Start.year for x in objList) // 10) * 10
            for year in range(startDecade, 2030, 10):
                labels.append(f"{year}")
                values.append(
                    sum(
                        ceil(
                            (x.Duration.seconds / 60)
                            * x.Length
                            * len([y for y in YearRange(x) if y in range(year, year + 11)])
                            / len(YearRange(x))
                        )
                        for x in objList
                        if set(range(year, year + 10)).intersection(set(YearRange(x)))
                    )
                )
        elif getattr(objList[0], "Year", None):
            startDecade = (min(x.Year for x in objList) // 10) * 10
            for year in range(startDecade, 2030, 10):
                labels.append(f"{year}s")
                values.append(
                    sum(x.Duration.seconds / 60 for x in objList if year <= x.Year < year + 10)
                )
        if labels and values:
            fig = px.pie(
                category_orders={"names": labels},
                hole=0.25,
                names=labels,
                title="Runtime Breakdown by Year",
                values=values,
            )

            outputDiv = GetHTML(fig, True)
            dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.simple_tag
def GenreBreakdown(objList: list, useCount: bool, force: bool) -> str:
    outputDiv = ""
    dstPath = GetDst(objList, f"GenreBreakdown{"-Count" if useCount else''}")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        results = {}
        gList = [y for y in DEFINED_TAGS["Genres"] if [x for x in objList if y in x.Genre_Tags]]
        colors = px.colors.qualitative.Plotly + px.colors.qualitative.Light24
        colorMap = dict(
            (DEFINED_TAGS["Genres"][idx], colors[idx]) for idx in range(len(DEFINED_TAGS["Genres"]))
        )

        genreSorted = sorted(
            gList,
            key=lambda y: len([x for x in objList if y in x.Genre_Tags]),
        )

        for genre in genreSorted:
            if genreEls := [x for x in objList if genre in x.Genre_Tags]:
                results[genre] = (
                    len(genreEls) if useCount else sum(x.Duration.seconds for x in genreEls)
                )
                objList = [x for x in objList if genre not in x.Genre_Tags]

        if results := dict(sorted(results.items(), key=lambda item: item[1], reverse=True)):
            fig = px.pie(
                category_orders={"names": list(results.keys())},
                hole=0.25,
                color=list(results.keys()),
                color_discrete_map=colorMap,
                names=list(results.keys()),
                title=f"{"Runtime" if not useCount else "Count"} by Genre",
                values=list(results.values()),
            )

            outputDiv = GetHTML(fig, True)
            dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.filter
def ValuesOverYears(objList: list, force: bool) -> str:
    outputDiv = ""
    dstPath = GetDst(objList, "ValuesOverYears")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        currentYear = datetime.datetime.now().year + 1
        years = []
        mediaCount = []
        watchStatus = []
        titles = []

        startDecade = min(x.Year for x in objList)

        for year in range(startDecade, currentYear, 1):
            w, d, n = Get3Types([x for x in objList if x.Year == year])
            years.append(year)
            mediaCount.append(len(w))
            watchStatus.append("Watched")
            titles.append("<br>".join([x.Title for x in w]))

            years.append(year)
            mediaCount.append(len(d))
            watchStatus.append("Downloaded")
            titles.append("<br>".join([x.Title for x in d]))

            years.append(year)
            mediaCount.append(len(n))
            watchStatus.append("Neither")
            titles.append("<br>".join([x.Title for x in n]))

        df = pd.DataFrame(
            data={
                "Year": years,
                "Media Counts": mediaCount,
                "Watch Status": watchStatus,
                "Titles": titles,
            }
        )
        if not df.empty:
            fig = px.bar(
                df,
                x="Year",
                y="Media Counts",
                color="Watch Status",
                hover_name="Titles",
                color_discrete_map=WATCH_COLOR_MAP,
            )

            fig.update_layout(
                barmode="stack",
                title="Watch Trends Over Time",
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5,
                ),
            )
            fig.update_xaxes(dtick=5)
            outputDiv = GetHTML(fig)
            dstPath.write_text(outputDiv, encoding="utf-8")

    return outputDiv


@register.filter
def TimeLine(objList: list, force: bool) -> str:
    dstPath = GetDst(objList, "TimeLine")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        objList = sorted(list(objList), key=lambda x: (x.Series_Start))
        data = []
        freeList: list[int] = []
        for obj in objList:
            yLevel = CalcIdx(obj, freeList)
            data.append(
                {
                    "Title": obj.Title,
                    "Series_Start": str(f"{obj.Series_Start}"),
                    "Series_End": str(
                        f"{obj.Series_End if obj.Series_End.year > MINIMUM_YEAR else 'now'}"
                    ),
                    "Watched": (
                        "Watched" if obj.Watched else "Downloaded" if obj.Downloaded else "Neither"
                    ),
                    "Idx": yLevel,
                }
            )
        df = pd.DataFrame(data)
        fig = px.timeline(
            data_frame=df,
            x_start="Series_Start",
            x_end="Series_End",
            y="Idx",
            color="Watched",
            color_discrete_map=WATCH_COLOR_MAP,
            hover_name="Title",
            title="Watching Trends over Time",
        )
        outputDiv = GetHTML(fig)
        dstPath.write_text(outputDiv, encoding="utf-8")

    return outputDiv


def YearPercentage(date):
    date = datetime.date.today() if date.year <= MINIMUM_YEAR else date
    # 04/06/2019
    return date.year + (date.month / 12) + (date.day / (31 * 12))


def Get3Types(objList):
    watched = [x for x in objList if x.Watched]
    downloaded = [x for x in objList if x.Downloaded and not x.Watched]
    neither = [x for x in objList if not x.Downloaded and not x.Watched]
    return watched, downloaded, neither


@register.filter
def GenreSearch(objList: list, force: bool):
    outputDiv = ""
    dstPath = GetDst(objList, "GenreSearch")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        genres = []
        mediaCount = []
        watchStatus = []
        counts = []
        typeStr = objList[0].__class__.__name__

        def GenreSort(g, objList) -> float:
            subList = [x for x in objList if g in x.Genre_Tags]
            types = Get3Types(subList)
            return len(types[0]) / len(subList) if subList else 0

        genreDict = {}
        for genre in sorted(
            DEFINED_TAGS["Genres"], key=lambda y: len([x for x in objList if y in x.Genre_Tags])
        ):
            genreDict[genre] = [x for x in objList if genre in x.Genre_Tags]
            objList = [x for x in objList if x not in genreDict[genre]]

        for genre in sorted(genreDict, key=lambda x: GenreSort(x, genreDict[x]), reverse=True):
            if genreList := genreDict[genre]:
                w, d, n = Get3Types(genreList)
                genres.append(genre)
                mediaCount.append(len(w) / len(genreList))
                watchStatus.append("Watched")
                counts.append(f"{len(w)}/{len(genreList)} {typeStr}s Watched")

                genres.append(genre)
                mediaCount.append(len(d) / len(genreList))
                watchStatus.append("Downloaded")
                counts.append(f"{len(d)}/{len(genreList)} {typeStr}s Downloaded")

                genres.append(genre)
                mediaCount.append(len(n) / len(genreList))
                watchStatus.append("Neither")
                counts.append(f"{len(n)}/{len(genreList)} {typeStr}s Unwatched")

        df = pd.DataFrame(
            data={
                "Genre": genres,
                "Watch %": mediaCount,
                "Watch Status": watchStatus,
                "Number": counts,
            }
        )
        if not df.empty:
            fig = px.bar(
                df,
                x="Genre",
                y="Watch %",
                color="Watch Status",
                hover_name="Number",
                color_discrete_map=WATCH_COLOR_MAP,
            )

            fig.update_layout(
                barmode="stack",
                title="Watch Trends Across Genres",
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5,
                ),
            )
            outputDiv = GetHTML(fig)
            dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.filter
def FancyRatings(objList: list, force: bool) -> str:
    dstPath = GetDst(objList, "FancyRatings")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        startDecade = min(x.Series_Start.year for x in objList)
        trimmedList = [x for x in objList if x.Watched]
        rollingTrend = ExtractRollingTrendRatings(startDecade, trimmedList)

        titles = []
        soloRatings = []
        soloYears = []
        genres = []
        for obj in sorted(trimmedList, key=lambda x: x.Series_End - x.Series_Start, reverse=True):
            titles.append(obj.Title)
            titles.append(obj.Title)
            soloRatings.append(obj.Rating)
            soloRatings.append(obj.Rating)
            soloYears.append(YearPercentage(obj.Series_Start))
            soloYears.append(YearPercentage(obj.Series_End))
            genres.append(obj.BiggestTag)
            genres.append(obj.BiggestTag)
        df = pd.DataFrame(
            {
                "Ratings": soloRatings,
                "Year": soloYears,
                "Title": titles,
                "Genre": genres,
            }
        )

        fig = px.line(
            data_frame=df,
            x="Year",
            y="Ratings",
            color="Genre",
            title="Rating Over Time",
            hover_name="Title",
            line_group="Title",
            markers=True,
        )
        fig.add_scatter(
            x=rollingTrend[:, 0],
            y=rollingTrend[:, 1],
            line={"dash": "dash"},
            name="Rolling Average",
        )
        fig.update_layout(showlegend=True)

        outputDiv = GetHTML(fig)
        dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


def YearRange(obj):
    endYear = (
        obj.Series_End.year + 1
        if obj.Series_End.year > MINIMUM_YEAR
        else datetime.datetime.now().year + 1
    )
    return range(obj.Series_Start.year, endYear)


def ExtractRollingTrendRatings(startDecade, trimmedObj):
    ratings = []
    years = []
    for i in list(range(startDecade, datetime.datetime.now().year + 1)):
        showsActive = [x for x in trimmedObj if i in YearRange(x)]
        if showsActive:
            years.append(i)
            ratings.append(sum(x.Rating for x in showsActive) / len(showsActive))
    rollingTrend = sm.nonparametric.lowess(ratings, years, frac=0.11)
    return rollingTrend


@register.filter
def DurationVsRating(objList: list, force: bool) -> str:
    dstPath = GetDst(objList, "DurationVsRating")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        trimmedList = [x for x in objList if x.Watched]
        trimmedList = sorted(trimmedList, key=lambda x: x.Year)
        useTotal = "Length" in dir(objList[0])
        duration = [
            (x.Duration.seconds / 60 if not useTotal else x.Total_Length) for x in trimmedList
        ]
        df = pd.DataFrame(
            {
                "Ratings": [x.Rating for x in trimmedList],
                "Duration": duration,
                "Title": [x.Title for x in trimmedList],
                "Decade": [str(x.Year // 10 * 10) for x in trimmedList],
            }
        )
        fig = px.scatter(
            df,
            x="Duration",
            y="Ratings",
            title="Duration vs Rating",
            color="Decade",
            log_x=useTotal,
            labels={"Duration": "Media Length", "Ratings": "Star Ratings"},
            hover_name="Title",
        )
        rollingTrend = sm.nonparametric.lowess(df["Ratings"], df["Duration"], frac=0.3)
        fig.add_scatter(x=rollingTrend[:, 0], y=rollingTrend[:, 1], mode="lines", name="Average")
        outputDiv = GetHTML(fig)
        dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.filter
def CompletionPercentageRuntime(objList: list, force: bool) -> str:
    dstPath = GetDst(objList, "CompletionPercentageVsRuntime")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        cats = [
            "Watched on MS",
            "Watched Streaming",
            "Downloaded",
            "Neither",
        ]
        df = pd.DataFrame(
            {
                "label": cats,
                "values": (
                    [
                        sum(
                            x.Duration.seconds // 60 for x in objList if x.Watched and x.Downloaded
                        ),
                        sum(
                            x.Duration.seconds // 60
                            for x in objList
                            if x.Watched and not x.Downloaded
                        ),
                        sum(
                            x.Duration.seconds // 60
                            for x in objList
                            if not x.Watched and x.Downloaded
                        ),
                        sum(
                            x.Duration.seconds // 60
                            for x in objList
                            if not x.Watched and not x.Downloaded
                        ),
                    ]
                    if "Total_Length" not in dir(objList[0])
                    else [
                        sum(x.Total_Length for x in objList if x.Watched and x.Downloaded),
                        sum(x.Total_Length for x in objList if x.Watched and not x.Downloaded),
                        sum(x.Total_Length for x in objList if not x.Watched and x.Downloaded),
                        sum(x.Total_Length for x in objList if not x.Watched and not x.Downloaded),
                    ]
                ),
            }
        )
        fig = px.pie(
            df,
            hole=0.25,
            names="label",
            color="label",
            color_discrete_map=WATCH_COLOR_MAP,
            category_orders={"label": cats},
            title="Watch Status by Duration",
            values="values",
        )

        outputDiv = GetHTML(fig, True)
        dstPath.write_text(outputDiv, encoding="utf-8")
    return outputDiv


@register.filter
def CompletionPercentage(objList: list, force: bool) -> str:
    dstPath = GetDst(objList, "CompletionPercentage")
    if dstPath.exists() and not force:
        outputDiv = dstPath.read_text(encoding="utf-8")
    else:
        cats = [
            "Watched on MS",
            "Watched Streaming",
            "Downloaded",
            "Neither",
        ]
        df = pd.DataFrame(
            {
                "label": cats,
                "values": (
                    [
                        len([x for x in objList if x.Watched and x.Downloaded]),
                        len([x for x in objList if x.Watched and not x.Downloaded]),
                        len([x for x in objList if not x.Watched and x.Downloaded]),
                        len([x for x in objList if not x.Watched and not x.Downloaded]),
                    ]
                ),
            }
        )
        fig = px.pie(
            df,
            hole=0.25,
            names="label",
            category_orders={"label": cats},
            color="label",
            color_discrete_map=WATCH_COLOR_MAP,
            title="Watch Status by Count",
            values="values",
        )

        outputDiv = GetHTML(fig, True)
        dstPath.write_text(outputDiv, encoding="utf-8")

    return outputDiv


def GetHTML(figure, isPie=False) -> str:

    figure.update_layout(
        paper_bgcolor="rgb(33, 37, 41)",
        plot_bgcolor="rgb(33, 37, 41)",
        template="plotly_dark",
        height=450 if isPie else 800,
        transition={"duration": 0},
    )
    return figure.to_html(full_html=False)


def CalcIdx(obj, yLevels: list) -> int:
    rangeObj = range(
        GetDateVal(obj.Series_Start),
        GetDateVal(obj.Series_End if obj.Series_End.year > MINIMUM_YEAR else datetime.date.today())
        + 1,
    )
    for idx, levelList in enumerate(yLevels):
        foundMatch = False
        for levelRange in reversed(levelList):
            if set(levelRange) & set(rangeObj):
                foundMatch = True
                break
        if not foundMatch:
            levelList.append(rangeObj)
            return idx
    yLevels.append([rangeObj])
    return len(yLevels) - 1


def GetDateVal(date: datetime.date):
    return date.year * 365 + date.month * 30 + date.day
