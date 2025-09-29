# /// script
# dependencies = [
#     "pywin32",
#     "progress",
#     "pyYaml"
# ]
# ///

import logging
import sys
import time
from pathlib import Path

import win32com.client as com

try:
    from django.conf import settings as django_settings

    SYNC = django_settings.SYNC_PATH
except ModuleNotFoundError:
    SYNC = Path(sys.argv[1])

from progress.bar import Bar
from yaml import Dumper, dump
from yaml import safe_load as load

LOGGER = logging.getLogger("UserLogger")


def GetMovies(parent: Path, showProgress: bool) -> list[dict]:
    path = parent / "Movies"
    objList = []
    progBar = None
    if showProgress:
        progBar = Bar(
            "Loading Movies...",
            max=len(list(path.glob("**/*.*"))),
            suffix=r"%(index)d/%(max)d - %(eta)ds",
        )
    for file in path.glob("**/*.*"):
        if file.is_file() and file.suffix not in [".ico", ".json", ".yml", ".srt"]:
            title = " ".join(file.stem.split(" ")[:-1])
            size = file.stat().st_size / (1024 * 1024 * 1024)
            year = file.stem.split(" ")[-1][1:-1]
            tags = [x for x in str(file.parent).replace(str(path), "").split("\\") if x != ""]
            obj = {
                "Title": title,
                "Year": year,
                "Size": round(size, 2),
                "Tags": tags,
                "FilePath": str(file),
            }
            if obj["Size"] == 0:
                obj["Size"] = 0.0001
            objList.append(obj)
        if showProgress and isinstance(progBar, Bar):
            progBar.next()
    if showProgress:
        print()
        print("Movies Complete")
    with (path / "Summary.yml").open(
        mode="w",
        encoding="utf-8",
    ) as fp:
        dump({"Movies": objList}, fp, Dumper)
    return objList


BANNED_COMPONENTS = ["season", "_", "special"]


def GetTV(parent: Path, showProgress: bool) -> list[dict]:
    path = parent / "TV Shows"
    folderObjs = []
    fso = com.Dispatch("Scripting.FileSystemObject")
    contents = list(path.glob("**/*"))
    folders = [x for x in contents if "." not in x.name and not FolderBanned(x)]
    subFiles = [x for x in contents if "." in x.name]
    progBar = None
    if showProgress:
        progBar = Bar(
            "Loading Shows...",
            max=len(folders),
            suffix=r"%(index)d/%(max)d - %(eta)ds",
        )
    for folder in folders:
        parents = [x for x in folders if str(x) + "\\" in str(folder) and x != folder]
        children = [x for x in folders if str(folder) + "\\" in str(x) and x != folder]
        if len(children) == 0:
            eps = [x for x in subFiles if str(folder) in str(x)]
            winF = fso.GetFolder(folder)
            folderObjs.append(
                {
                    "Title": folder.stem,
                    "FilePath": str(folder),
                    "Count": len(eps),
                    "Tags": [x.stem for x in parents],
                    "Size": round(winF.Size / (1024 * 1024 * 1024), 2),
                },
            )
        if showProgress and isinstance(progBar, Bar):
            progBar.next()  # ty: ignore[possibly-unresolved-reference]
    if showProgress:
        print()
        print("TV Complete")
    if folderObjs:
        with Path(path / "Summary.yml").open("w", encoding="utf-8") as fp:
            dump(folderObjs, fp, Dumper)
    return folderObjs


def FolderBanned(pathObj: Path) -> bool:
    return any(x.lower() in str(pathObj).lower() for x in BANNED_COMPONENTS)


def RipWDrive(mediaType: str, showProgress: bool) -> None:
    try:
        ms = Path(r"\\192.168.0.100") if not Path("Z:\\").exists() else Path("Z:\\")
        start = time.time()
        movies = []
        tv = []
        if mediaType == "Movie":
            movies = GetMovies(ms, showProgress)
            LOGGER.info("Movie scrape took %f seconds", time.time() - start)
        else:
            tv = GetTV(ms, showProgress)
            LOGGER.info("TV scrape took %f seconds", time.time() - start)
        summaryFile = SYNC / "config" / "MediaServerSummary.yml"
        currentFile = {}
        with summaryFile.open(encoding="utf-8") as fp:
            currentFile = load(fp)
        with Path(SYNC / "config" / "MediaServerSummary.yml").open(
            mode="w",
            encoding="utf-8",
        ) as fp:
            dump(
                {
                    "Movies": movies if mediaType == "Movie" and movies else currentFile["Movies"],
                    "TV Shows": tv if mediaType != "Movie" and tv else currentFile["TV Shows"],
                },
                fp,
                Dumper,
            )
    except FileNotFoundError as e:
        print(f"Drive not found {e}")


if __name__ == "__main__":
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))
    RipWDrive("TV Show", True)
    RipWDrive("Movie", True)
