import keyboard


import game_threads
game_threads.Player.exit_pressed = True
keyboard.press('q')


def test_of_player():
    try:
        player = game_threads.Player(4, 5, 0, game_threads.player_image)
        if player:
            print("---------------------------------Test Player complete--------------------------------------------------")
            return 200
        else:
            print("------------------------------------Test Player Failed---------------------------------------------")
            return 0
    except NameError:
        return print("-------------------------------Test Player Failed NameError-------------------------------------")
    except AttributeError:
        return print("--------------------------Test Player Failed Attribute Error------------------------------------")


def test_of_walls():
    player = game_threads.Player(4, 5, 0, game_threads.player_image)
    walls = []
    for x in range(0, 9):
        wall = game_threads.Wall(x, x, game_threads.wall_image)
        walls.append(wall)
    x_mem, y_mem = player.x, player.y
    player.forward()
    walls_position = []
    for wall in walls:
        walls_position.append([wall.x, wall.y])

    if player.x == x_mem and player.y == y_mem:
        print("--------------------------------Test of walls complete-------------------------------------------------")
        print(walls)
        return 200
    else:
        print("---------------------------------Test of walls failed--------------------------------------------------")
        return 0


def test_bullet():
    bot = game_threads.Bot(1, 1, 180, game_threads.bot_image)
    player = game_threads.Player(1, 5, 0, game_threads.player_image)
    bot.bot_shoot()
    player.shoot()
    if game_threads.bot_bullet.x != 0 and game_threads.bullet.x != 0:
        print("---------------------------------Test bullet complete--------------------------------------------------")
        return 200
    else:
        print("----------------------------------Test bullet failed---------------------------------------------------")
        return 0


test_bullet()
test_of_walls()
test_of_player()