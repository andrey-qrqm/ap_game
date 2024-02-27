#import game_threads
import cutscene

cutscene.cutscene(
        text="Well, you've opened my game. Good Luck and try to win it",
        songfile="song_1.wav",
        imagefile="title.png",
    )

game = open('./game_threads.py')

exec(game.read())
game.close()
#game_threads.cv2.destroyAllWindows()
cutscene.cutscene(
    text="Well, you've killed my bot. Wanna restart? Press 'e' to restart or 'q' to exit",
    songfile="song_1.wav",
    imagefile="title.png",
)
