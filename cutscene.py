"""
Download example music file from opengameart.org
"""
import string
from pygame import mixer
import cv2


def cutscene(text: str, songfile: str, imagefile: str, wait: int = 3):
    # start music
    mixer.init()
    mixer.music.load(songfile)
    mixer.music.play(loops=-1)
    mixer.music.set_volume(0.5)

    # show the image
    img = cv2.imread(imagefile)  # sometimes returns None
    assert img is not None
    # show text
    img[-100:] = 0
    img = cv2.putText(
        img,
        text[:47],
        org=(15, 490),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.75,
        color=(255, 255, 255),
        thickness=2,
    )
    img = cv2.putText(
        img,
        text[47:],
        org=(15, 530),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.75,
        color=(255, 255, 255),
        thickness=2,
    )
    cv2.imshow("Cutscene", img)

    # wait for user input\
    i = 0
    while True:
        i += 1
        key = chr(cv2.waitKey(1) & 0xFF)
        if key in string.printable:
            cv2.destroyAllWindows()
            mixer.music.stop()
            return key
        # time.sleep (wait)


if __name__ == "__main__":
    cutscene(
        text="Congratulations Warrior, you just completed the level. Now the real challenge starts.",
        songfile="./visual/song_1.wav",
        imagefile="./visual/title.png",
    )

    cutscene(
        text="Welcome To The New Level ",
        wait=5,
        songfile="./visual/song_1.wav",
        imagefile="./visual/title.png",
    )