import json
import os.path
import time
from pathlib import Path


def GetMovies(parent):
    path = parent / "Movies"
    objList = []
    for file in path.glob("**/*.*"):
        if file.is_file() and file.suffix not in [".ico", ".json"]:
            title = " ".join(file.stem.split(" ")[:-1])
            size = os.stat(file).st_size / (1024 * 1024 * 1024)
            year = file.stem.split(" ")[-1][1:-1]
            tags = [x for x in str(file.parent).replace(str(path), "").split("\\") if x != ""]
            obj = {"Title": title, "Year": year, "Size": round(size, 2), "Tags": tags}
            objList.append(obj)
    with open(path / "Summary.json", encoding="ascii", mode="w") as fp:
        json.dump({"Movies": objList}, fp)
    return objList


def GetTV(parent):
    path = parent / "TV Shows"
    objList = {}
    for file in path.glob("**/*.*"):
        if file.is_file() and file.suffix not in [".ico", ".json"]:
            showPath = str(file.parent).replace(str(path) + "\\", "").split("\\Season", 1)[0]
            showName = showPath.split("\\")[-1]
            if showName not in objList:
                objList[showName] = {
                    "Count": 1,
                    "Tags": showPath.split("\\")[:-1],
                    "Size": os.stat(file).st_size,
                }
                # print(showName, objList[showName])
            else:
                objList[showName]["Count"] = objList[showName]["Count"] + 1
                objList[showName]["Size"] = objList[showName]["Size"] + os.stat(file).st_size
    with open(path / "Summary.json", encoding="ascii", mode="w") as fp:
        json.dump({"TV Show": objList}, fp)
    return objList


if __name__ == "__main__":
    start = time.time()
    movies = GetMovies(Path(r"W:\\"))
    print("Movies Done")
    print(time.time() - start)
    start = time.time()
    tv = GetTV(Path(r"W:\\"))
    print(time.time() - start)
    with open(
        r".\Projects\PersonalSite\DjangoSite\static\files\MediaServerSummary.json",
        mode="w",
        encoding="ascii",
    ) as fp:
        json.dump({"Movies": movies, "TV Shows": tv}, fp)
