import datetime
from math import ceil

import pandas as pd
import plotly.express as px  # type:ignore
import statsmodels.api as sm  # type:ignore
from django import template

from ..utils import MINIMUM_YEAR

register = template.Library()


@register.filter
def RatingOverTime(objList: list) -> str:
    outputDiv = ""
    df = None
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
            range_y=(0, 10.5),
            title="Rating Over Time",
            hover_name="Title",
            color="Duration",
            color_continuous_scale="rainbow",
        )
        rollingTrend = sm.nonparametric.lowess(df["Rating"], df["Release Year"], frac=0.2)

        fig.add_scatter(
            x=rollingTrend[:, 0],
            y=rollingTrend[:, 1],
            mode="lines",
        )
        fig.update_layout(showlegend=False)

        outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def DurationOverTime(objList: list) -> str:
    outputDiv = ""
    df = None

    useTotal = getattr(objList[0], "Total_Length", None) is not None
    if useTotal:
        df = pd.DataFrame(
            {
                "Title": [x.Title for x in objList],
                "Year": [x.Series_Start.year for x in objList],
                "Duration": [x.Total_Length for x in objList],
                "Watched": [x.Watched for x in objList],
            }
        )
    else:
        df = pd.DataFrame(
            {
                "Title": [x.Title for x in objList],
                "Year": [x.Year for x in objList],
                "Duration": [x.Duration.seconds / 60 for x in objList],
                "Watched": [x.Watched for x in objList],
            }
        )
    if df is not None:
        fig = px.scatter(
            df,
            x="Year",
            y="Duration",
            color=df["Watched"].map({True: "Watched", False: "Not Watched"}),
            color_discrete_map={
                "Not Watched": "red",
                "Watched": "blue",
            },
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
    return outputDiv


@register.filter
def DecadeBreakdown(objList: list) -> str:
    outputDiv = ""
    labels = []
    values = []
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
            title="Release Decade Breakdown by Year",
            values=values,
        )
        outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def RuntimeBreakdown(objList: list) -> str:
    outputDiv = ""
    labels = []
    values = []

    if getattr(objList[0], "Series_Start", None):
        startDecade = (min(x.Series_Start.year for x in objList) // 10) * 10
        for year in range(startDecade, 2030, 10):
            labels.append(f"{year}")
            values.append(
                sum(
                    ceil(
                        (x.Duration.seconds / 60)
                        * x.Length
                        * len(
                            [
                                y
                                for y in range(x.Series_Start.year, x.Series_End.year + 1)
                                if y in range(year, year + 11)
                            ]
                        )
                        / len(range(x.Series_Start.year, x.Series_End.year + 1))
                    )
                    for x in objList
                    if set(range(year, year + 10)).intersection(
                        set(range(x.Series_Start.year, x.Series_End.year + 1))
                    )
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

        outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def ValuesOverYears(objList: list) -> str:
    outputDiv = ""
    currentYear = datetime.datetime.now().year + 1
    years = []
    mediaCount = []
    watchStatus = []
    titles = []

    startDecade = min(x.Year for x in objList)

    for year in range(startDecade, currentYear, 1):
        years.append(year)
        mediaCount.append(len([x for x in objList if x.Year == year and x.Watched]))
        watchStatus.append("Watched")
        titles.append("<br>".join([x.Title for x in objList if x.Year == year and x.Watched]))

        years.append(year)
        mediaCount.append(
            len([x for x in objList if x.Year == year and not x.Watched and x.Downloaded])
        )
        watchStatus.append("Downloaded")
        titles.append(
            "<br>".join(
                [x.Title for x in objList if x.Year == year and not x.Watched and x.Downloaded]
            )
        )

        years.append(year)
        mediaCount.append(
            len([x for x in objList if x.Year == year and not x.Watched and not x.Downloaded])
        )
        watchStatus.append("Not Watched or Downloaded")
        titles.append(
            "<br>".join(
                [x.Title for x in objList if x.Year == year and not x.Watched and not x.Downloaded]
            )
        )

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
            color_discrete_sequence=[
                "blue",
                "lightgreen",
                "red",
            ],
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
    return outputDiv


@register.filter
def TimeLine(objList: list) -> str:
    objList = sorted(list(objList), key=lambda x: (x.Series_Start))
    data = []
    freeList: list[int] = []
    for _idx, obj in enumerate(objList):
        yLevel = CalcIdx(obj, freeList)
        data.append(
            {
                "Title": obj.Title,
                "Series_Start": str(f"{obj.Series_Start}"),
                "Series_End": str(
                    f"{obj.Series_End if obj.Series_End.year > MINIMUM_YEAR else 'now'}"
                ),
                "Watched": (
                    "Watched"
                    if obj.Watched
                    else "Downloaded" if obj.Downloaded else "Not Watched or Downloaded"
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
        color=df["Watched"].map(
            {
                "Watched": "Watched",
                "Not Watched or Downloaded": "Not Watched",
                "Downloaded": "Downloaded",
            }
        ),
        color_discrete_map={
            "Not Watched": "red",
            "Watched": "blue",
            "Downloaded": "lightgreen",
        },
        hover_name="Title",
        title="Watching Trends over Time",
    )
    outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def FancyRatings(objList: list) -> str:
    startDecade = min(x.Series_Start.year for x in objList)
    trimmedObj = [x for x in objList if x.Watched]
    ratings = []
    years = []
    sizes = []
    shows = []
    for i in range(startDecade, datetime.datetime.now().year + 1):
        showsActive = [
            x
            for x in trimmedObj
            if i
            in range(
                x.Series_Start.year,
                (
                    x.Series_End.year + 1
                    if x.Series_End.year > MINIMUM_YEAR
                    else datetime.datetime.now().year + 1
                ),
            )
        ]
        if showsActive:
            years.append(i)
            ratings.append(sum(x.Rating for x in showsActive) / len(showsActive))
            sizes.append(len(showsActive))
            shows.append("<br>".join(sorted([x.Title for x in showsActive])))
    df = pd.DataFrame(
        {
            "Ratings": ratings,
            "Year": years,
            "Number of Shows": sizes,
            "Shows Active": shows,
        }
    )

    fig = px.scatter(
        df,
        x="Year",
        y="Ratings",
        title="Yearly Average Rating Over Time",
        size="Number of Shows",
        hover_name="Shows Active",
    )
    rollingTrend = sm.nonparametric.lowess(df["Ratings"], df["Year"], frac=0.12)

    fig.add_scatter(
        x=rollingTrend[:, 0],
        y=rollingTrend[:, 1],
        mode="lines",
    )
    fig.update_layout(showlegend=False)

    outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def DurationVsRating(objList: list) -> str:
    trimmedList = [x for x in objList if x.Watched]
    trimmedList = sorted(trimmedList, key=lambda x: x.Year)
    useTotal = "Length" in dir(objList[0])
    duration = [(x.Duration.seconds / 60 if not useTotal else x.Total_Length) for x in trimmedList]
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
        range_y=(0, 10.5),
        color="Decade",
        log_x=useTotal,
        labels={"Duration": "Media Length", "Ratings": "Star Ratings"},
        hover_name="Title",
    )
    rollingTrend = sm.nonparametric.lowess(df["Ratings"], df["Duration"], frac=0.3)
    fig.add_scatter(x=rollingTrend[:, 0], y=rollingTrend[:, 1], mode="lines", name="Average")
    outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def CompletionPercentageRuntime(objList: list) -> str:
    cats = [
        "Watched on MS",
        "Watched Streaming",
        "Ready On MS",
        "Not Watched or Downloaded",
    ]
    df = pd.DataFrame(
        {
            "label": cats,
            "values": (
                [
                    sum(x.Duration.seconds // 60 for x in objList if x.Watched and x.Downloaded),
                    sum(
                        x.Duration.seconds // 60 for x in objList if x.Watched and not x.Downloaded
                    ),
                    sum(
                        x.Duration.seconds // 60 for x in objList if not x.Watched and x.Downloaded
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
        category_orders={"label": cats},
        title=f"Watch Status by Duration",
        values="values",
    )

    outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def CompletionPercentage(objList: list) -> str:
    cats = [
        "Watched on MS",
        "Watched Streaming",
        "Ready On MS",
        "Not Watched or Downloaded",
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
        title=f"Watch Status by Count",
        values="values",
    )

    outputDiv = GetHTML(fig)
    return outputDiv


def GetHTML(figure) -> str:

    figure.update_layout(
        paper_bgcolor="rgb(33, 37, 41)",
        plot_bgcolor="rgb(33, 37, 41)",
        template="plotly_dark",
    )
    return figure.to_html(full_html=False)


def CalcIdx(obj, yLevels: list) -> int:
    endPoint = GetDateVal(
        obj.Series_End if obj.Series_End.year > MINIMUM_YEAR else datetime.date.today()
    )
    startPoint = GetDateVal(obj.Series_Start)
    daysList = list(range(startPoint, endPoint + 1))
    for idx, slot in enumerate(yLevels):
        if not any(x in slot for x in daysList):
            slot += daysList
            return idx
    yLevels.append(daysList)
    return len(yLevels) - 1


def GetDateVal(date: datetime.date):
    return date.year * 365 + date.month * 30 + date.day
