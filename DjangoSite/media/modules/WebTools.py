import concurrent.futures
import datetime
import os
import random
import re
import time
from datetime import timedelta

import requests
from progress.bar import Bar  # type:ignore
from wikipedia import wikipedia  # type:ignore

from ..models import Movie, TVShow

apiEndpoint = r"https://en.wikipedia.org/w/api.php?format=json"
ua = {"User-Agent": "Aedan McHale (aedan.mchale@gmail.com)"}

wikiDescriptionTags = {Movie: "_(film)", TVShow: "_(TV_series)"}


def GetCorrectPage(title):
    newPage = title.replace(" ", "_")
    statusCode = 500
    attempt = 0
    while (newPage == title.replace(" ", "_") or statusCode > 210) and attempt < 5:
        time.sleep(1)

        getTextLink = apiEndpoint + f"&action=parse&section=0&prop=text&page={newPage}"
        r = requests.get(getTextLink, headers=ua)
        statusCode = r.status_code

        if "error" in r.json():
            attempt += 1
            newPage = title.split("_")[0].replace(" ", "_")
            statusCode = 404
            continue

        page = str(r.json()["parse"]["text"]["*"])
        searchLen = len('<p>Redirect to:</p><ul class="redirectText"><li><a href="/wiki/')
        redirectSearch = (
            page.find('<p>Redirect to:</p><ul class="redirectText"><li><a href="/wiki/') + searchLen
        )

        if redirectSearch != searchLen - 1:
            attempt += 1
            redirectEnd = page.find('"', redirectSearch)
            newPage = page[redirectSearch:redirectEnd]
            continue
        break
    if attempt >= 5:
        newPage = None
    return newPage


def GetShowInfo(wikiLink, mediaType) -> str:
    details = []
    with open("output.txt", "w") as fp:
        fp.write(f"Run at {datetime.datetime.now()}\n\n\n")
    if wikiLink:
        wikiLink = (
            wikiLink.replace("https://en.wikipedia.org/wiki/", "")
            if "wikipedia" in wikiLink
            else wikiLink
        )
        wikiLink = GetCorrectPage(wikiLink)
        details.append(ScrapeWiki(wikiLink=wikiLink))
    elif mediaType:
        with Bar("Submitting...", max_len=(mediaType.objects.all()).count()) as bar:
            # pool = concurrent.futures.ThreadPoolExecutor()
            for selected in mediaType.objects.all():
                if selected.NeedsUpdate:
                    print()
                    print(selected.NeedsUpdate)
                    details.append(UpdateDetails(selected, mediaType))
                bar.next()
            # pool.shutdown(wait=True)
            print("Finished")
    outStr = ""
    for d in details:
        outStr += f"{d}\n"
    return outStr


def UpdateDetails(selected, mediaType) -> tuple:
    details = None
    print(selected.Title)

    wikiLink = (
        selected.Title + wikiDescriptionTags[mediaType]
        if selected.InfoPage == "None"
        else selected.InfoPage.split("/wiki/")[-1]
    )

    wikiLink = GetCorrectPage(title=wikiLink)
    if (
        wikiLink
        and selected.InfoPage in ["None", r"http://127.0.0.1:8000/media"]
        or f"https://en.wikipedia.org/wiki/{wikiLink}" != selected.InfoPage
    ):
        selected.InfoPage = f"https://en.wikipedia.org/wiki/{wikiLink}"
        selected.save()
        print("Info Page Saved")

    if selected.Logo in ["logos/DefaultIMG.png", "None"] and wikiLink:
        try:
            editMade = False
            used = []
            details = ScrapeWiki(wikiLink=wikiLink)
            if (
                hasattr(selected, "Year")
                and selected.Year != int(details[1])
                and details[1]
                and "ng=" not in details[1]
            ):
                selected.Year = int(details[1])
                used.append("year")
                editMade = True
            if (
                hasattr(selected, "Duration")
                and selected.Duration != details[2]
                and details[2]
                and type(details[2]) == timedelta
            ):
                selected.Duration = details[2]
                editMade = True
                used.append("time")
            if (
                selected.Logo in ["logos/DefaultIMG.png", "None"]
                and details[3]
                and "http" in details[3]
                and "https:s=" not in details[3]
            ):
                selected.Logo = details[3]
                used.append("Logo")
                editMade = True

            if selected.Logo == "None":
                print("No Image Found")
                with open("output.txt", "a") as fp:
                    fp.write(f"LOGO -- {selected}\n")

            if editMade:
                selected.save()
                print(f"Details Saved {details} {used}")
            elif selected.Logo != "None":
                with open("output.txt", "a") as fp:
                    fp.write(f"{selected}\n")

        except (TypeError, ValueError) as err:
            print("Save failed due to " + str(err))
    if wikiLink == None:
        selected.InfoPage = "None"
        print("No Page Found")
        selected.save()
    print()

    return (selected, details)


def ScrapeWiki(wikiLink) -> tuple:
    title = wikiLink.split("/wiki/")[-1]
    getTextLink = apiEndpoint + f"&action=parse&section=0&prop=text&page={title}"
    r = requests.get(getTextLink, headers=ua)
    title, year, runTime, imageLink = None, None, None, None
    if r.status_code == 200 and "parse" in r.json():
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
