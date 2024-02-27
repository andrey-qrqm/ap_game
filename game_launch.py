#import game_threads
import cutscene

cutscene.cutscene(
        text="Welcome! Or you are not new here? I can't remember all of you... Good luck defeating my bot!",
        songfile="./visual/song_1.wav",
        imagefile="./visual/title.png",
    )

game = open('./game_threads.py')

exec(game.read())
game.close()
#game_threads.cv2.destroyAllWindows()
cutscene.cutscene(
    text="Well, you've killed my bot or decided to quit my game. Wanna restart? Press 'e' to restart or 'q' to exit",
    songfile="./visual/song_1.wav",
    imagefile="./visual/title.png",
)
