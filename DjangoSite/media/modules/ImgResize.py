from pathlib import Path

from PIL import Image


def RemoveAlpha(png):
    try:
        background = Image.new("RGBA", png.size, (0, 0, 0))
        print(png.size, background.size)
        alphaComp = Image.alpha_composite(background, png)
        return alphaComp

    except ValueError:
        print(f"{png} Failed")
        return png


def ResizeImages(parentDir):
    parentDir = Path(parentDir)
    if parentDir.exists():
        for img in parentDir.glob("*.png"):
            background = Image.new("RGBA", color="black", size=(320, 240))
            currentImg = Image.open(img)
            currentImg = RemoveAlpha(currentImg)
            background.paste(
                currentImg,
                (
                    ((320 - currentImg.width) // 2),
                    ((240 - currentImg.height) // 2),
                ),
            )
            background.save(str(img))


ResizeImages(
    r"C:\mysources\Aedan\PersonalScripts\Projects\PersonalSite\DjangoSite\static\logos\tvshows\ToReshape"
)
