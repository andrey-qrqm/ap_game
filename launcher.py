key = 'e'
while key == 'e':
    game = open('./game_launch.py')
    exec(game.read())
    game.close()
    key = input("e or q")
    print(key)
