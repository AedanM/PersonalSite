from pathlib import Path

from PIL import Image


def RemoveAlpha(path: Path):
    png = Image.open(path)
    try:
        background = Image.new("RGBA", png.size, (0, 0, 0))
        alphaComp = Image.alpha_composite(background, png)
        return alphaComp

    except ValueError:
        print(f"{path} Failed")
        return png


def ResizeImages(parentDir):
    parentDir = Path(parentDir)
    if parentDir.exists():
        for img in parentDir.glob("*.png"):
            print(img)
            SingleResize(img)


def SingleResize(img):
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


ResizeImages(r"D:\PersonalSite\DjangoSite\static\logos\tvshows\toReshape")
