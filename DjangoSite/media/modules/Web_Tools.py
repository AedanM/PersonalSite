import random
import re
from datetime import timedelta

import requests
from wikipedia import wikipedia  # type:ignore

from ..models import Movie, TVShow

apiEndpoint = r"https://en.wikipedia.org/w/api.php?format=json"
ua = {"User-Agent": "Aedan McHale (aedan.mchale@gmail.com)"}

wikiDescriptionTags = {Movie: "_(film)", TVShow: "_(TV_series)"}


def GetCorrectPage(title):
    newPage = title
    statusCode = 500
    while newPage == title and statusCode > 210:
        getTextLink = apiEndpoint + f"&action=parse&section=0&prop=text&page={newPage}"
        r = requests.get(getTextLink, headers=ua)
        statusCode = r.status_code
        page = str(r.json()["parse"]["text"]["*"])
        redirectSearch = page.find(
            '<p>Redirect to:</p><ul class="redirectText"><li><a href="/wiki/'
        ) + len('<p>Redirect to:</p><ul class="redirectText"><li><a href="/wiki/')

        if redirectSearch > 0:
            redirectEnd = page.find('"', redirectSearch)
            newPage = page[redirectSearch:redirectEnd]
    return newPage


def GetShowInfo(wikiLink) -> str:
    if wikiLink:
        wikiLink = (
            wikiLink.replace("https://en.wikipedia.org/wiki/", "")
            if "wikipedia" in wikiLink
            else wikiLink
        )
    else:
        selected = random.choice(Movie.objects.all())
        wikiLink = selected.Title + wikiDescriptionTags[Movie]
    wikiLink = GetCorrectPage(wikiLink)
    # return wikiLink
    details = ScrapeWiki(wikiLink=wikiLink)
    outStr = wikiLink + "\n"
    for d in details:
        outStr += f"{d}\n"
    return outStr


def ScrapeWiki(wikiLink) -> tuple:
    title = wikiLink.split("/wiki/")[-1]
    getTextLink = apiEndpoint + f"&action=parse&section=0&prop=text&page={title}"
    r = requests.get(getTextLink, headers=ua)
    title, year, runTime, imageLink = None, None, None, None
    if r.status_code == 200:
        j = str(r.json()["parse"]["text"]["*"])
        with open("temp.html", "w", encoding="utf-8") as fp:
            fp.write(j)

        infoBoxStart = j.find('<table class="infobox vevent">')
        altSearch = False
        if infoBoxStart < 0:
            infoBoxStart = j.find('<table class="infobox ib-tv vevent">')
            altSearch = True

        timeEnd = j.find(" minutes", infoBoxStart)
        if timeEnd > 0:
            timeStr = re.sub(r"\D", "", j[timeEnd - 3 : timeEnd])
            runTime = timedelta(minutes=int(timeStr))

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

        imgSearch = '<img src="'
        imageStart = j.find(imgSearch, infoBoxStart) + len(imgSearch)
        imageEnd = j.find('"', imageStart)
        imageLink = "https:" + j[imageStart:imageEnd]

    return title, year, runTime, imageLink
