"""
Proof-of-concept: move around on a 2D grid

Install dependencies:

    pip install opencv-python
"""


### LIBRARY ARCADE


import threading
import time
import walls_generator
import cv2
import numpy as np
from pynput import keyboard as kb

i = 0
bullet_lock = threading.Lock()
bot_bullet_lock = threading.Lock()

class MyException(Exception): pass


class Player:
    exit_pressed = False

    def __init__(self, x, y, direction, image, exit_pressed):
        self.x = x
        self.y = y
        self.direction = direction
        self.image = image
        self.exit_pressed = exit_pressed

    def forward(self):
        global bot, player
        if self.direction == 0 and self.y > 0:
            if not is_wall(self.x, self.y - 1) and not is_bot(self.x, self.y - 1, bot) and not is_player(self.x, self.y - 1, player):
                self.y -= 1
        elif self.direction == 90 and self.x < 9:
            if not is_wall(self.x + 1, self.y) and not is_bot(self.x + 1, self.y, bot) and not is_player(self.x + 1, self.y, player):
                self.x += 1
        elif self.direction == 180 and self.y < 9:
            if not is_wall(self.x, self.y + 1) and not is_bot(self.x, self.y + 1, bot) and not is_player(self.x, self.y + 1, player):
                self.y += 1
        elif self.direction == 270 and self.x > 0:
            if not is_wall(self.x - 1, self.y) and not is_bot(self.x - 1, self.y, bot) and not is_player(self.x - 1, self.y, player):
                self.x -= 1
        print("position - ", self.x, self.y)
        return self

    def backward(self):
        if self.direction == 0 and self.y < 9 and not is_wall(self.x, self.y + 1):
            self.y += 1
        elif self.direction == 90 and self.x > 0:
            if not is_wall(self.x - 1, self.y):
                self.x -= 1
        elif self.direction == 180 and self.y > 0:
            if not is_wall(self.x, self.y - 1):
                self.y -= 1
        elif self.direction == 270 and self.x < 9:
            if not is_wall(self.x + 1, self.y):
                self.x += 1
        #print("position - ", self.x, self.y)
        return self

    def rotate_a(self):
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.direction -= 90
        if self.direction < 0: self.direction += 360
        print(self.direction)
        return self

    def rotate_d(self):
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        self.direction += 90
        if self.direction > 270: self.direction -= 360
        print(self.direction)
        # print("d was pressed")
        return self

    # move - reading the keyboard and changing the x and y of the player
    # return - player
    # function to detect how to move forward based on direction
    def shoot(self):
        global bullet_moving, bullet
        with bullet_lock:
            if not bullet_moving:
                bullet_moving = True
                # bullet.direction = self.direction
                bullet = Bullet(self.x, self.y, bullet_image, self.direction)
                threading.Thread(target=self._move_bullet, args=(bullet,), daemon=True).start()

    def _move_bullet(self, bullet):
        global bullet_moving
        while bullet_moving and not self.exit_pressed:
            bullet.move()
            time.sleep(1 / 30)
            with bullet_lock:
                if bullet.move():
                    bullet_moving = False
                    print("COLLIDE!!!!")
                    break
        bullet_moving = False


class Bot(Player):
    def bot_move(self):
        while not exit_pressed:
            time.sleep(1)
            x_mem = self.x
            y_mem = self.y
            self.forward()
            if self.x == x_mem and self.y == y_mem:
                self.rotate_d()
                self.rotate_d()
                self.bot_shoot()
        pass


    def bot_shoot(self):
        global bot_bullet_moving, bot_bullet
        print("BOT IS SHOOTING")
        with bot_bullet_lock:
            if not bot_bullet_moving:
                bot_bullet_moving = True
                # bullet.direction = self.direction
                bot_bullet = Bullet(self.x, self.y, bullet_image, self.direction)
                print("start position of bot bullet is - ", bot_bullet.x, bot_bullet.y, bot_bullet.direction)
                threading.Thread(target=self._bot_move_bullet, args=(bot_bullet,), daemon=True).start()


    def _bot_move_bullet(self, bot_bullet):
        global bot_bullet_moving
        while bot_bullet_moving and not self.exit_pressed:
            bot_bullet.move()
            if bot_bullet.move():
                bot_bullet.on_collide()
            time.sleep(1 / 30)
            with bot_bullet_lock:
                if bot_bullet.move():
                    bot_bullet_moving = False

                    print("COLLIDE!!!!")
                    break
        bot_bullet_moving = False



class Wall:
    def __init__(self, x, y, image):
        global walls
        self.x = x
        self.y = y
        self.image = image
        walls.append(self)


# constants measured in pixel
class Bullet:
    def __init__(self, x, y, image, direction, speed=0.25):
        self.x = x
        self.y = y
        # self.speed = speed
        self.image = image
        self.direction = direction
        self.speed = speed

    # function of processing the bullet moving
    def move(self):
        collide = False
        if self.direction == 0:
            if not is_wall(self.x, self.y - 1) and self.y > 0:
                self.y -= self.speed
                time.sleep(1 / 30)
            else:
                collide = True
        elif self.direction == 90:
            if not is_wall(self.x + 1, self.y) and self.x < 9:
                self.x += self.speed
                time.sleep(1 / 30)
            else:
                collide = True
        elif self.direction == 180:
            if not is_wall(self.x, self.y + 1) and self.y < 9:
                self.y += self.speed
                time.sleep(1 / 30)
            else:
                collide = True
        elif self.direction == 270:
            if not is_wall(self.x - 1, self.y) and self.x > 0:
                self.x -= self.speed
                time.sleep(1 / 30)
            else:
                collide = True
        return collide

    def on_collide(self):
        global player, bot
        if self.x == player.x and self.y == player.y:
            print("++++BOT SHOT PLAYER++++")

        elif self.x == bot.x and self.y == bot.y:
            print("++++PLAYER SHOT BOT++++")
        else:
            pass


# one frame drawing
def screen_renew(background, player, bot):
    global bullet, bot_bullet
    while not player.exit_pressed:
        draw_player(background, player, bullet, bot)
        # Update the bullet's position if it's moving
        if bullet_moving:
            bullet.move()
        if bot_bullet_moving:
            bot_bullet.move()
        key = cv2.waitKey(10)
        time.sleep(1 / 60)
        if key == 27 or player.exit_pressed:
            break


# auto-renewable of a screen every 300ms
def draw_player(background, player, bullet, bot):
    """draws the player image on the screen"""
    frame = background.copy()
    #print("position of the bullet: ", bullet.x, bullet.y)
    # print("drawing player at ", player.x, player.y)
    xpos, ypos = player.x * TILE_SIZE, player.y * TILE_SIZE
    frame[ypos: ypos + TILE_SIZE, xpos: xpos + TILE_SIZE] = player.image
    bot_x, bot_y = bot.x * TILE_SIZE, bot.y * TILE_SIZE
    frame[bot_y: bot_y + TILE_SIZE, bot_x: bot_x + TILE_SIZE] = bot_image
    for wall in walls:
        xpos, ypos = wall.x * TILE_SIZE, wall.y * TILE_SIZE
        frame[ypos: ypos + TILE_SIZE, xpos: xpos + TILE_SIZE] = wall.image
    if bullet_moving:
        xpos, ypos = int(bullet.x * TILE_SIZE), int(bullet.y * TILE_SIZE)
        frame[ypos: ypos + TILE_SIZE, xpos: xpos + TILE_SIZE] = bullet.image
    if bot_bullet_moving:
        xpos, ypos = int(bot_bullet.x * TILE_SIZE), int(bot_bullet.y * TILE_SIZE)
        frame[ypos: ypos + TILE_SIZE, xpos: xpos + TILE_SIZE] = bullet_image
    cv2.imshow("frame", frame)
    cv2.waitKey(10)


# single screen drawing with static pos
def double_size(img):
    """returns an image twice as big"""
    return np.kron(img, np.ones((2, 2, 1), dtype=img.dtype))


def is_wall(x, y):
    flag = False
    for wall in walls:
        if int(wall.x) == int(x) and int(wall.y) == int(y):
            flag = True
            break
    return flag


def is_bot(x, y, bot):
    if x == bot.x and y == bot.y:
        return True


def is_player(x, y, player):
    if x == player.x and y == player.y:
        return True


# function of processing a keyboard input
def on_press(key):
    global player
    # time.sleep(1)
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))

        if key.char == 'w':
            print('player forward detected')
            player.forward()

        if key.char == 's':
            print('player backward detected')
            player.backward()

        if key.char == 'a':
            print('player rotate A detected')
            player.rotate_a()

        if key.char == 'd':
            print('player rotate D detected')
            player.rotate_d()
        if key.char == 'q':
            player.exit_pressed = True
            return False

        if key.char == 'e':
            print("SHOOT!")
            player.shoot()
            return bullet

        if key == kb.Key.esc:
            # Stop listener
            player.exit_pressed = True
            return False
    except AttributeError:
        print('special key {0} pressed'.format(
            key))
        if key == kb.Key.esc:
            # Stop listener
            return False


def on_release(key):
    pass


# function of starting a game
def start():
    thread_screen = threading.Thread(target=screen_renew, args=(background, player, bot), daemon=True)
    thread_bot = threading.Thread(target=bot.bot_move, daemon=True)
    thread_bot.start()
    thread_screen.start()
    with kb.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
    thread_screen.join()
    thread_bot.join()
    cv2.destroyAllWindows()

# function of creating walls on the level
def wall_show():
    wall_num = walls_generator.generate_level()
    print("wall_num", wall_num)
    for wall in wall_num:
        wall_create = Wall(wall[0], wall[1], wall_image)

# screen size and tile size definition
SCREEN_SIZE_X, SCREEN_SIZE_Y = 640, 640
TILE_SIZE = 64

# load images
bot_image = double_size(cv2.imread("tiles/dragon.png"))
player_image = double_size(cv2.imread("tiles/deep_elf_high_priest.png"))
wall_image = double_size(cv2.imread("tiles/wall.png"))
bullet_image = double_size(cv2.imread("tiles/ring.png"))
background = np.zeros((SCREEN_SIZE_Y, SCREEN_SIZE_X, 3), np.uint8)
# create black background image with BGR color channels

xpos, ypos = 4, 4
direction = 0
# starting position and direction of the player in dungeon


walls = []  # ARRAY OF TYPE Wall

# create a player object
player = Player(xpos, ypos, 0, player_image, False)
# create a bot object
bot = Bot(1, 1, 0, bot_image, False)

# create a walls object
#wall_show()

# creating bullets
bullet = Bullet(0, 0, bullet_image, 0)
bot_bullet = Bullet(0, 0, bullet_image, 0)

exit_pressed = False
bullet_moving = False
bot_bullet_moving = False
print(player.exit_pressed)

print("WALLS - ", walls)
# start()