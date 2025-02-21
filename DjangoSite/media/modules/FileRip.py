import json
import logging
import os.path
import sys
import time
from pathlib import Path

from progress.bar import Bar

LOGGER = logging.getLogger("UserLogger")


def GetMovies(parent, showProgress: bool):
    path = parent / "Movies"
    objList = []
    if showProgress:
        progBar = Bar(
            "Loading Movies...",
            max=len(list(path.glob("**/*.*"))),
            suffix=r"%(index)d/%(max)d - %(eta)ds",
        )
    for file in path.glob("**/*.*"):
        if file.is_file() and file.suffix not in [".ico", ".json"]:
            title = " ".join(file.stem.split(" ")[:-1])
            size = os.stat(file).st_size / (1024 * 1024 * 1024)
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
        if showProgress:
            progBar.next() # type: ignore
    if showProgress:
        print()
        print("Movies Complete")
    with open(path / "Summary.json", encoding="ascii", mode="w") as fp:
        json.dump({"Movies": objList}, fp)
    return objList


BANNED_COMPONENTS = ["season", "_", "special"]


def GetTV(parent: Path, showProgress: bool):
    path = parent / "TV Shows"
    folderObjs = []
    if showProgress:
        progBar = Bar(
            "Loading Shows...",
            max=len(list(path.glob("**/*/"))),
            suffix=r"%(index)d/%(max)d - %(eta)ds",
        )
    for folder in path.glob("**/*/"):
        subFolders = [str(x).lower() for x in folder.glob("**/*/")]
        useFolder = True
        if not FolderBanned(folder):
            for subF in subFolders:
                if not FolderBanned(subF):  # All subFolders must be banned
                    useFolder = False
                    break
            if useFolder:
                subFiles = list(folder.glob("**/*.*"))
                folderObjs.append(
                    {
                        "Title": folder.stem,
                        "FilePath": str(folder),
                        "Count": len(subFiles),
                        "Tags": [
                            x
                            for x in str(folder).replace(str(path), "").split("\\")[:-1]
                            if x != ""
                        ],
                        "Size": round(
                            sum(f.stat().st_size for f in subFiles) / (1024 * 1024 * 1024), 2
                        ),
                    }
                )
        if showProgress:
            progBar.next() # type: ignore
    if showProgress:
        print()
        print("TV Complete")
    if folderObjs:
        with (path / "Summary.json").open("w", encoding="utf-8") as fp:
            json.dump(folderObjs, fp)
    return folderObjs


def FolderBanned(pathObj):
    return any(x.lower() in str(pathObj).lower() for x in BANNED_COMPONENTS)


def RipWDrive(mediaType: str, showProgress: bool):
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
        summaryFile = Path(r"C:\Sync\WebsiteShare") / "MediaServerSummary.json"
        currentFile = json.loads(summaryFile.read_text())
        with open(
            Path(r"C:\Sync\WebsiteShare") / "MediaServerSummary.json",
            mode="w",
            encoding="ascii",
        ) as fp:
            json.dump(
                {
                    "Movies": movies if mediaType == "Movie" and movies else currentFile["Movies"],
                    "TV Shows": tv if mediaType != "Movie" and tv else currentFile["TV Shows"],
                },
                fp,
            )
    except FileNotFoundError as e:
        print(f"Drive not found {e}")


if __name__ == "__main__":
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))
    RipWDrive("TV Show", True)
    RipWDrive("Movie", True)
