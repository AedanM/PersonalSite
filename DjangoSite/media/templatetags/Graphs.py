import datetime

import pandas as pd
import plotly.express as px
import statsmodels.api as sm
from django import template

register = template.Library()


@register.filter
def RatingOverTime(objList):
    outputDiv = ""
    df = None
    if getattr(objList[0], "Year", None):
        df = pd.DataFrame(
            {
                "Title": [x.Title for x in objList if x.Watched],
                "Release Year": [x.Year for x in objList if x.Watched],
                "Rating": [x.Rating for x in objList if x.Watched],
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
def DurationOverTime(objList):
    outputDiv = ""
    df = None

    if getattr(objList[0], "Year", None):
        df = pd.DataFrame(
            {
                "Title": [x.Title for x in objList],
                "Year": [x.Year for x in objList],
                "Duration": [x.Duration.seconds / 60 for x in objList],
                "Watched": [x.Watched for x in objList],
            }
        )
    else:
        df = pd.DataFrame(
            {
                "Title": [x.Title for x in objList],
                "Year": [x.Series_Start.year for x in objList],
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
def DecadeBreakdown(objList):
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
def RuntimeBreakdown(objList):
    outputDiv = ""
    labels = []
    values = []
    if getattr(objList[0], "Year", None):
        startDecade = (min(x.Year for x in objList) // 10) * 10
        for year in range(startDecade, 2030, 10):
            labels.append(f"{year}s")
            values.append(
                sum(x.Duration.seconds / 60 for x in objList if year <= x.Year < year + 10)
            )
    elif getattr(objList[0], "Series_Start", None):
        startDecade = (min(x.Series_Start.year for x in objList) // 10) * 10
        for year in range(startDecade, 2030, 10):
            labels.append(f"{year}s")
            values.append(
                sum(
                    (x.Duration.seconds / 60) * x.Length
                    for x in objList
                    if year <= x.Series_Start.year < year + 10
                )
            )
    if labels and values:
        fig = px.pie(
            category_orders={"names": labels},
            hole=0.25,
            names=labels,
            title="Runtime Breakdown by Year",
            values=values,
        )
        fig.update_traces(hoverinfo="label+percent", textinfo="value")

        outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def WatchOverYears(objList):
    outputDiv = ""
    currentYear = datetime.datetime.now().year + 1
    years = []
    mediaCount = []
    watchStatus = []
    titles = []
    if getattr(objList[0], "Year", None):
        startDecade = min(x.Year for x in objList)

        for year in range(startDecade, currentYear, 1):
            years.append(year)
            mediaCount.append(len([x for x in objList if x.Year == year and x.Watched]))
            watchStatus.append("Watched")
            titles.append("<br>".join([x.Title for x in objList if x.Year == year and x.Watched]))

            years.append(year)
            mediaCount.append(len([x for x in objList if x.Year == year and not x.Watched]))
            watchStatus.append("Not Watched")
            titles.append(
                "<br>".join([x.Title for x in objList if x.Year == year and not x.Watched])
            )
    elif getattr(objList[0], "Series_Start", None):
        startDecade = min(x.Series_Start for x in objList).year
        for year in range(startDecade, currentYear, 1):
            years.append(year)
            mediaCount.append(
                len([x for x in objList if x.Series_Start.year == year and x.Watched])
            )
            watchStatus.append("Watched")
            titles.append(
                "<br>".join([x.Title for x in objList if x.Series_Start.year == year and x.Watched])
            )

            years.append(year)
            mediaCount.append(
                len([x for x in objList if x.Series_Start.year == year and not x.Watched])
            )
            watchStatus.append("Not Watched")
            titles.append(
                "<br>".join(
                    [x.Title for x in objList if x.Series_Start.year == year and not x.Watched]
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
        )

        fig.update_layout(
            barmode="stack",
            title="Watching Trends Over Time",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.2,
                xanchor="center",
                x=0.5,
            ),
        )
        fig.update_xaxes(dtick=5)
        outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def TimeLine(objList):
    objList = sorted(list(objList), key=lambda x: x.Series_Start)
    data = []
    for idx, obj in enumerate(objList):
        data.append(
            {
                "Title": obj.Title,
                "Series_Start": f"{obj.Series_Start}",
                "Series_End": f"{obj.Series_End if obj.Series_End.year > 1900 else 'now'}",
                "Watched": obj.Watched,
                "Idx": idx,
            }
        )
    df = pd.DataFrame(data)
    fig = px.timeline(
        data_frame=df,
        x_start="Series_Start",
        x_end="Series_End",
        y="Idx",
        color=df["Watched"].map({True: "Watched", False: "Not Watched"}),
        color_discrete_map={
            "Not Watched": "red",
            "Watched": "blue",
        },
        hover_name="Title",
        title="Watching Trends over Time",
    )
    outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def FancyRatings(objList):
    startDecade = min(x.Series_Start.year for x in objList)
    trimmedObj = [x for x in objList if x.Watched]
    ratings = []
    years = []
    sizes = []
    shows = []
    for i in range(startDecade, datetime.datetime.now().year):
        showsActive = [
            x
            for x in trimmedObj
            if i
            in range(
                x.Series_Start.year,
                (x.Series_End.year if x.Series_End.year > 1900 else datetime.datetime.now().year),
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
    rollingTrend = sm.nonparametric.lowess(df["Ratings"], df["Year"], frac=0.3)

    fig.add_scatter(
        x=rollingTrend[:, 0],
        y=rollingTrend[:, 1],
        mode="lines",
    )
    fig.update_layout(showlegend=False)

    outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def DurationVsRating(objList):
    trimmedList = [x for x in objList if x.Watched]
    trimmedList = sorted(trimmedList, key=lambda x: x.Year)

    duration = [
        x.Duration.seconds / 60 if "Length" not in dir(x) else x.Total_Length.seconds / 60
        for x in trimmedList
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
        range_y=(0, 10.5),
        color="Decade",
        labels={"Duration": "Media Length", "Ratings": "Star Ratings"},
        hover_name="Title",
    )
    rollingTrend = sm.nonparametric.lowess(df["Ratings"], df["Duration"], frac=0.3)
    fig.add_scatter(x=rollingTrend[:, 0], y=rollingTrend[:, 1], mode="lines", name="Average")

    outputDiv = GetHTML(fig)
    return outputDiv


@register.filter
def CompletionPercentage(objList, field):

    if field == "Watched":
        objList = [x for x in objList if x.Watched or x.Downloaded]
    df = pd.DataFrame(
        {
            "label": [field, f"Not {field}"],
            "values": (
                [
                    sum(x.Duration.seconds // 60 for x in objList if getattr(x, field)),
                    sum(x.Duration.seconds // 60 for x in objList if not getattr(x, field)),
                ]
                if "Total_Length" not in dir(objList[0])
                else [
                    sum(x.Total_Length.seconds // 60 for x in objList if getattr(x, field)),
                    sum(x.Total_Length.seconds // 60 for x in objList if not getattr(x, field)),
                ]
            ),
        }
    )
    fig = px.pie(
        df,
        hole=0.25,
        names="label",
        category_orders={"label": [field, f"Not {field}"]},
        title=f"Completion Percentage for {field} Material",
        values="values",
    )

    outputDiv = GetHTML(fig)
    return outputDiv


def GetHTML(figure):

    figure.update_layout(
        paper_bgcolor="rgb(33, 37, 41)",
        plot_bgcolor="rgb(33, 37, 41)",
        # plot_bgcolor="rgba(100,100,100,255)",
        # font_color="whitesmoke",
        template="plotly_dark",
    )
    return figure.to_html(full_html=False)
