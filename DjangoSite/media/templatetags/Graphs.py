import plotly.express as px
from django import template

register = template.Library()


@register.filter
def RatingOverTime(objList):
    outputDiv = ""
    if getattr(objList[0], "Year", None):
        fig = px.scatter(
            labels={
                "y": "Rating",
                "x": "Release Year",
            },
            range_y=(0, 5.5),
            title="Movie Rating Over Time",
            trendline="lowess",
            trendline_options=dict(frac=0.1),
            x=[x.Year for x in objList if x.Rating > 0],
            y=[x.Rating / 2 for x in objList if x.Rating > 0],
            hover_name=[x.Title for x in objList if x.Rating > 0],
        )
        outputDiv = fig.to_html(full_html=False)
    return outputDiv


@register.filter
def DurationOverTime(objList):
    outputDiv = ""
    if getattr(objList[0], "Year", None):
        fig = px.scatter(
            labels={
                "y": "Duration",
                "x": "Release Year",
            },
            title="Movie Duration Over Time",
            hover_name=[x.Title for x in objList],
            trendline="lowess",
            trendline_options=dict(frac=0.1),
            x=[x.Year for x in objList],
            y=[(x.Duration.seconds / 60) for x in objList],
        )
        outputDiv = fig.to_html(full_html=False)
    return outputDiv


@register.filter
def DecadeBreakdown(objList):
    outputDiv = ""
    if getattr(objList[0], "Year", None):
        startDecade = (min(x.Year for x in objList) // 10) * 10
        labels = []
        values = []
        for year in range(startDecade, 2030, 10):
            labels.append(f"{year}s")
            values.append(len([x for x in objList if x.Year >= year and x.Year < year + 10]))
        fig = px.pie(
            category_orders={"names": labels},
            hole=0.25,
            names=labels,
            title="Movie Release Decade Breakdown by Year",
            values=values,
        )
        outputDiv = fig.to_html(full_html=False)
    return outputDiv


@register.filter
def RuntimeBreakdown(objList):
    outputDiv = ""
    if getattr(objList[0], "Year", None):
        startDecade = (min(x.Year for x in objList) // 10) * 10
        labels = []
        values = []
        for year in range(startDecade, 2030, 10):
            labels.append(f"{year}s")
            values.append(
                sum(
                    x.Duration.seconds / 60
                    for x in objList
                    if x.Year >= year and x.Year < year + 10
                )
            )
        fig = px.pie(
            category_orders={"names": labels},
            hole=0.25,
            names=labels,
            title="Movies Runtime Breakdown by Year",
            values=values,
        )
        fig.update_traces(hoverinfo="label+percent", textinfo="value")

        outputDiv = fig.to_html(full_html=False)
    return outputDiv
