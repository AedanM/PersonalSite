import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class Folder:
    Name: str
    Level: int
    Parent: "Folder | None"
    ParentList: list = field(default_factory=list)


def ParseMediaFiles(className: str, filePath):
    fList = GetAllFiles(className=className, filePath=filePath)
    with open("mid.txt", "w") as fp:
        fp.write("\n\n".join([("\t" * x.Level) + str(x) for x in fList]))
    treedict = GenDepends(fList)
    with open("out.txt", "w") as fp:
        fp.write("\n\n".join([("\t" * x.Level) + str(x) for x in fList]))
    return "\n\n".join([("\t" * x.Level) + str(x) for x in fList])


def GetAllFiles(className: str, filePath):
    tree = ET.parse(filePath)
    listTree = [(x.attrib["name"], x.tag.replace("folder", "")) for x in tree.iter()]
    parentDir = Folder("root", 1, None)
    fList = []
    for item in tree.iter():
        level = int(item.tag.replace("folder", ""), 10)
        name = item.attrib["name"]
        p = parentDir
        while p.Level != level - 1 and p.Parent != None:
            p = p.Parent  # type:ignore
        fList.append(Folder(Name=name, Level=level, Parent=p))
        parentDir = Folder(Name=name, Level=level, Parent=p)
    return fList


def GenDepends(fileList):
    for file in fileList:
        p = file.Parent
        while p.Name != "root":
            file.ParentList.append(p.Name)
            p = p.Parent
        file.ParentList = [x for x in file.ParentList if x != "W"]


def FormatDir(d, depth):
    s = ""
    for i, j in d.items():
        s += "\t" * depth + " " + i + "\n"
        s += FormatDir(j, depth + 1)
    return s


def FindDepth(d: dict, s: str):
    if s in d.keys():
        return d[s]
    else:
        for i in d.keys():
            found = FindDepth(d[i], s)
            if found:
                return found
        return -1


def FindElements(path):
    obj = [
        (el.attrib["name"], int(el.tag.replace("folder", "")))
        for el in ET.parse(source=path).iter()
    ]
    CurrentIdx = [0] * 10
    masterList = [["root"]]
    for name, level in obj:
        dest = masterList
        for i in range(0, level, 1):
            dest = dest[CurrentIdx[i]]
        dest.append([name])  # type:ignore
        CurrentIdx[level] = dest.index([name])  # type:ignore
    return masterList[0][1]


def FormatListOfLists(l, depth=0):
    s = ""
    for listEl in l:
        if type(listEl) == str:
            s += "\t" * depth + listEl + "\n"
        elif type(listEl) == list[str]:
            s += "\t" * depth + "\n".join(listEl)
        else:
            s += "\t" * depth + FormatListOfLists(listEl, depth + 1)
    return s
