import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag

API_ENDPOINT = r"https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "Aedan McHale (aedan.mchale@gmail.com)"}


def GetByHeader(table: BeautifulSoup, header: str, regex: str) -> str | None:
    element: list[Tag] = [x for x in table.find_all("tr") if header in x.text]
    if element:
        tag = element[0].find("td")
        if tag:
            matches = re.findall(regex, tag.text)
            if matches:
                return matches[0]
    return None


def ScrapeWiki(wikiLink: str) -> dict:
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

    r = requests.get(API_ENDPOINT, params, headers=UA, timeout=1000)
    if r.status_code == 200:
        s = BeautifulSoup(r.content, features="html.parser")
        infoTables = s.find_all("table")
        if len(infoTables) > 1:
            infoTables = [x for x in infoTables if "infobox" in str(x)]

        if infoTables:
            infoBox = infoTables[0]

            if infoBox.find("tr"):
                out["Title"] = infoBox.find("tr").text

            GetLogo(out, infoBox)

            out["Duration"] = GetByHeader(infoBox, "Running time", r"\d+")
            if out["Duration"]:
                out["Duration"] = out["Duration"] + ":00"

            out["Year"] = GetByHeader(infoBox, "Release date", r"\d{4}")
            out["Length"] = GetByHeader(infoBox, "of episodes", r"\d+")

            genres = GetByHeader(infoBox, "Genre", r".+")
            if genres:
                out["Genre_Tags"] = ", ".join([x for x in genres.split(r"\n") if x])

            GetDates(out, infoBox)

    return out


def GetLogo(out: dict, infoBox: BeautifulSoup) -> None:
    try:
        # todo: check function
        imageLink = str(infoBox.find("img")["srcset"])  # pyright: ignore[reportOptionalSubscript, reportArgumentType]
        imageLink = r"https:" + bytes(imageLink, "utf-8").decode("unicode_escape")
        out["Logo"] = imageLink.replace('"', "")
    except (KeyError, TypeError):
        out["Logo"] = None


def GetDates(out: dict, infoBox: BeautifulSoup) -> None:
    datesElement = [x for x in infoBox.find_all("tr") if "Release" in x.text]
    dates = []
    for d in datesElement:
        dates += [
            datetime.strptime(x, "%Y-%m-%d") for x in re.findall(r"\d{4}-\d{1,2}-\d{1,2}", d.text)
        ]
    if dates:
        dates = sorted(dates)
        out["Series_Start"] = dates[0].strftime(r"%d/%m/%Y")
        out["Series_End"] = dates[-1].strftime(r"%d/%m/%Y")
