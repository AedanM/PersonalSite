import datetime
import re

import requests

from ..models import Movie, TVShow  # type:ignore

API_ENDPOINT = r"https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "Aedan McHale (aedan.mchale@gmail.com)"}

wikiDescriptionTags = {Movie: "_(film)", TVShow: "_(TV_series)"}


def GetImageLink(pageLink) -> str:
    outStr = ""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": pageLink,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }
    r = requests.get(url, params=params, headers=UA, timeout=1000)
    if r.status_code == 200 and "query" in r.json():
        try:
            outStr = list(r.json()["query"]["pages"].values())[0]["imageinfo"][0]["url"]
        except KeyError:
            outStr = "None Found"
    return outStr


def ScrapeWiki(wikiLink) -> dict:
    title = wikiLink.split("/wiki/")[-1]
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "section": "0",
        "format": "json",
    }
    r = requests.get(API_ENDPOINT, params, headers=UA, timeout=1000) # type: ignore
    title, year, runTime, imageLink, epLength = None, None, None, None, None
    if r.status_code == 200 and "parse" in r.json():
        j = str(r.json()["parse"]["text"]["*"])

        infoBoxStart = j.find('<table class="infobox vevent">')
        altSearch = False
        if infoBoxStart < 0:
            infoBoxStart = j.find('<table class="infobox ib-tv vevent">')
            altSearch = True

        timeEnd = j.find(" minutes", infoBoxStart)
        if timeEnd > 0:
            timeStr = re.sub(r"\D", "", j[timeEnd - 3 : timeEnd])
            runTime = datetime.timedelta(minutes=int(timeStr))

        titleSearchStr = (
            'style="font-size: 125%; font-style: italic;">'
            if not altSearch
            else r'class="infobox-above summary"><i>'
        )
        titleStart = j.find(
            (titleSearchStr),
            infoBoxStart,
        ) + len(titleSearchStr)

        titleEnd = j.find("</", titleStart)
        title = j[titleStart:titleEnd]

        dateStart = j.find('class="bday dtstart published updated itvstart">', infoBoxStart) + len(
            'class="bday dtstart published updated itvstart">'
        )
        year = j[dateStart : dateStart + 4]

        imgSearch = '<a href="/wiki/'
        imageStart = j.find(imgSearch, infoBoxStart) + len(imgSearch)
        imageEnd = j.find('"', imageStart)
        imageLink = GetImageLink(j[imageStart:imageEnd])

        epStart = j.find("of episodes", infoBoxStart)
        epStart = j.find('">', epStart) + len('">')
        epEnd = j.find("</", epStart)

        epLength = int(j[epStart:epEnd]) if j[epStart:epEnd].isnumeric() else -1

    return {
        "Title": title,
        "Year": year,
        "Duration": runTime,
        "Logo": imageLink,
        "InfoPage": wikiLink,
        "Length": epLength,
    }
