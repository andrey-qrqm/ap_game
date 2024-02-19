import game_threads
import cutscene

cutscene.cutscene(
        text="Well, you've opened my game. Good Luck and try to win it",
        songfile="song_1.wav",
        imagefile="title.png",
    )
game_threads.start()
