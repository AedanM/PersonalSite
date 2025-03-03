import logging
import sys
from pathlib import Path

from PIL import Image

LOGGER = logging.getLogger("UserLogger")


def RemoveAlpha(path: Path):
    png = Image.open(path)
    try:
        background = Image.new("RGBA", png.size, (0, 0, 0))
        alphaComp = Image.alpha_composite(background, png)
        return alphaComp

    except ValueError:
        LOGGER.warning("%s Failed To Remove Alpha", path)
        return png


def ResizeImages(parentDir):
    parentDir = Path(parentDir)
    if parentDir.exists():
        for img in parentDir.glob("*.png"):
            BackgroundResize(img)
    else:
        LOGGER.error("No parent dir %s", parentDir)


def BackgroundResize(img):
    currentImg = RemoveAlpha(img)
    background = Image.new("RGBA", color=currentImg.getpixel((0, 0)), size=(320, 240))
    background.paste(
        currentImg,
        (
            ((320 - currentImg.width) // 2),
            ((240 - currentImg.height) // 2),
        ),
    )
    background.save(str(img))


if __name__ == "__main__":
    ResizeImages(sys.argv[1])
