import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag

API_ENDPOINT = r"https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "Aedan McHale (aedan.mchale@gmail.com)"}


def GetByHeader(table, header, regex) -> str | None:
    element: list[Tag] = [x for x in table.find_all("tr") if header in x.text]
    if element:
        tag = element[0].find("td")
        if tag:
            matches = re.findall(regex, tag.text)
            if matches:
                return matches[0]  # type: ignore
    return None


def ScrapeWiki(wikiLink) -> dict:
    title = wikiLink.split("/wiki/")[-1]
    if "http" not in wikiLink:
        wikiLink = r"https://en.wikipedia.org/wiki/" + title
    out: dict[str, str | None] = {
        "Duration": None,
        "Genre_Tags": None,
        "InfoPage": wikiLink,
        "Length": None,
        "Logo": None,
        "Series_End": None,
        "Series_Start": None,
        "Title": None,
        "Year": None,
    }

    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "section": "0",
        "format": "json",
    }

    r = requests.get(API_ENDPOINT, params, headers=UA, timeout=1000)  # type: ignore
    if r.status_code == 200:
        s = BeautifulSoup(r.content, features="html.parser")
        infoTables = s.find_all("table")
        if len(infoTables) > 1:
            infoTables = [x for x in infoTables if "Infobox" in x.text]
        if infoTables:
            infoBox = infoTables[0]

            if infoBox.find("tr"):
                out["Title"] = infoBox.find("tr").text

            try:
                imageLink = infoBox.find("img")["srcset"]
                imageLink = r"https:" + bytes(imageLink, "utf-8").decode("unicode_escape")
                out["Logo"] = imageLink.replace('"', "")
            except (AttributeError, TypeError):
                out["Logo"] = None

            out["Duration"] = GetByHeader(infoBox, "Running time", r"\d+")

            out["Year"] = GetByHeader(infoBox, "Release date", r"\d{4}")

            out["Length"] = GetByHeader(infoBox, "of episodes", r"\d+")

            genres = GetByHeader(infoBox, "Genre", r".+")
            if genres:
                print(genres)
                out["Genre_Tags"] = ", ".join([x for x in genres.split(r"\n") if x])

            datesElement = [x for x in infoBox.find_all("tr") if "Release" in x.text]
            dates = []
            for d in datesElement:
                dates += [
                    datetime.strptime(x, "%Y-%m-%d")
                    for x in re.findall(r"\d{4}-\d{1,2}-\d{1,2}", d.text)
                ]
            if dates:
                dates = sorted(dates)  # type: ignore
                out["Series_Start"] = dates[0].strftime(r"%d/%m/%y")
                out["Series_End"] = dates[-1].strftime(r"%d/%m/%y")

    return out
