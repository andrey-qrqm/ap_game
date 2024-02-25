import game_threads
import cutscene

cutscene.cutscene(
        text="Well, you've opened my game. Good Luck and try to win it",
        songfile="song_1.wav",
        imagefile="title.png",
    )
game_threads.start(game_threads.player,
                   game_threads.bot,
                   game_threads.bullet,
                   game_threads.bot_bullet,
                   game_threads.bullet_moving,
                   game_threads.bot_bullet_moving)

key = cutscene.cutscene(
    text="Well, you've killed my bot. Wanna restart? Press 'e' to restart or 'q' to exit",
    songfile="song_1.wav",
    imagefile="title.png",
)
'''
print(key)
if key == 'e':
    game_threads.start(game_threads.player,
                       game_threads.bot,
                       game_threads.bullet,
                       game_threads.bot_bullet,
                       game_threads.bullet_moving,
                       game_threads.bot_bullet_moving)
    key = cutscene.cutscene(
    text="Well, you've killed my bot. Wanna restart? Press 'e' to restart or 'q' to exit",
    songfile="song_1.wav",
    imagefile="title.png",
)
'''