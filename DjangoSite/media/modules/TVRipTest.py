import json
import os
from pathlib import Path
from pprint import pp

from progress import bar

BANNED_COMPONENTS = ["season", "_", "special"]


def RipTV(parent: Path):
    path = parent / "TV Shows"
    folderObjs = []
    with bar.Bar(
        "Scanning",
        max=len(list(path.glob("**/*/"))),
        suffix="%(percent).1f%% - %(eta)ds",
    ) as b:
        for folder in path.glob("**/*/"):
            b.next()
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


def FolderBanned(pathObj):
    return any(x.lower() in str(pathObj).lower() for x in BANNED_COMPONENTS)


if __name__ == "__main__":
    p = Path(r"Z:\\")
    RipTV(p)
