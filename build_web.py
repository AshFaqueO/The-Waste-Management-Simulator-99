"""Build the browser version of TWMS'99 with pygbag.

Usage:  python build_web.py
Output: web/build/web/index.html (+ web.apk)  and  web/build/web.zip (upload this to itch.io)

It copies the game into web/main.py, shrinks images to the sizes the game
actually draws them at, converts mp3 -> ogg (browsers handle ogg reliably),
then runs pygbag.
"""
import os
import shutil
import subprocess
import sys

from PIL import Image
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
SRC_ASSETS = os.path.join(ROOT, "assets")
OUT_ASSETS = os.path.join(WEB, "assets")

# max size each image needs (the game scales them to these or smaller)
IMAGE_SIZES = {
    "sopbg.png": (1060, 690),
    "pinebarrens.png": (1060, 690),
    "logo.png": (1000, 320),
}
DEFAULT_SPRITE_SIZE = (300, 300)


def main():
    if os.path.exists(WEB):
        shutil.rmtree(WEB)
    os.makedirs(OUT_ASSETS)

    shutil.copy(os.path.join(ROOT, "TWMS99.py"), os.path.join(WEB, "main.py"))

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for name in sorted(os.listdir(SRC_ASSETS)):
        src = os.path.join(SRC_ASSETS, name)
        if name.lower().endswith(".png"):
            img = Image.open(src)
            img.thumbnail(IMAGE_SIZES.get(name, DEFAULT_SPRITE_SIZE), Image.LANCZOS)
            img.save(os.path.join(OUT_ASSETS, name), optimize=True)
        elif name.lower().endswith(".mp3"):
            dst = os.path.join(OUT_ASSETS, name[:-4] + ".ogg")
            # the long music track gets a lower bitrate to keep the download small
            quality = "2" if name == "Do.mp3" else "4"
            subprocess.run(
                [ffmpeg, "-y", "-loglevel", "error", "-i", src,
                 "-c:a", "libvorbis", "-q:a", quality, "-ar", "44100", dst],
                check=True,
            )

    subprocess.run(
        [sys.executable, "-m", "pygbag", "--build", "--archive",
         "--title", "The Waste Management Simulator 99", WEB],
        check=True,
    )
    print("\nDone. Open web/build/web/index.html via a local server, or upload web/build/web.zip to itch.io")


if __name__ == "__main__":
    main()
