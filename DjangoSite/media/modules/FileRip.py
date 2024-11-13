import json
import logging
import os.path
import time
from pathlib import Path

LOGGER = logging.getLogger("UserLogger")


def GetMovies(parent):
    path = parent / "Movies"
    objList = []
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

    with open(path / "Summary.json", encoding="ascii", mode="w") as fp:
        json.dump({"Movies": objList}, fp)
    return objList


BANNED_COMPONENTS = ["season", "_", "special"]


def GetTV(parent: Path):
    path = parent / "TV Shows"
    folderObjs = []

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
                        "Size": sum(f.stat().st_size for f in subFiles) / (1024 * 1024 * 1024),
                    }
                )
    with (path / "Summary.json").open("w", encoding="utf-8") as fp:
        json.dump(folderObjs, fp)
    return folderObjs


def FolderBanned(pathObj):
    return any(x.lower() in str(pathObj).lower() for x in BANNED_COMPONENTS)


def RipWDrive():
    if Path(r"W:\\").exists():
        start = time.time()
        movies = GetMovies(Path(r"W:\\"))
        LOGGER.info("Movie scrape took %f seconds", time.time() - start)
        start = time.time()
        tv = GetTV(Path(r"W:\\"))
        LOGGER.info("TV scrape took %f seconds", time.time() - start)
        with open(
            Path(__file__).parent.parent.parent / r"static\files\MediaServerSummary.json",
            mode="w",
            encoding="ascii",
        ) as fp:
            json.dump({"Movies": movies, "TV Shows": tv}, fp)


if __name__ == "__main__":
    RipWDrive()
