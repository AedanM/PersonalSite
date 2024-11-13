import os
from pathlib import Path
from pprint import pp

BANNED_COMPONENTS = ["season", "_", "special"]


def RipTV(parent: Path):
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
                folderObjs.append(
                    {
                        "Title": folder.stem,
                        "FilePath": str(folder),
                        "Count": len(list(folder.glob("**/*.*"))),
                        "Tags": [
                            x
                            for x in str(folder).replace(str(path), "").split("\\")[:-1]
                            if x != ""
                        ],
                        "Size": os.stat(folder).st_size / (1024 * 1024 * 1024),
                    }
                )
    pp(folderObjs)


def FolderBanned(pathObj):
    return any(x.lower() in str(pathObj).lower() for x in BANNED_COMPONENTS)


if __name__ == "__main__":
    p = Path(r"C:\Temp\MediaServerStandIn")
    RipTV(p)
