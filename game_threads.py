"""
Proof-of-concept: move around on a 2D grid

Install dependencies:

    pip install opencv-python
"""


### LIBRARY ARCADE
import random
import threading
import cutscene
import time

import game_threads
import walls_generator
import cv2
import math
import numpy as np
from pynput import keyboard as kb

bullet_lock = threading.Lock()
bot_bullet_lock = threading.Lock()


class MyException(Exception): pass


class Player:
    exit_pressed = False

    def __init__(self, x, y, direction, image):
        self.x = x
        self.y = y
        self.direction = direction
        self.image = image


    # player move forward
    def forward(self):
        global bot, player
        if self.direction == 0 and self.y > 0:
            if not is_wall(self.x, self.y - 1) and not is_bot(self.x, self.y - 1) and not is_player(self.x, self.y - 1):
                self.y -= 1
        elif self.direction == 90 and self.x < 9:
            if not is_wall(self.x + 1, self.y) and not is_bot(self.x + 1, self.y) and not is_player(self.x + 1, self.y):
                self.x += 1
        elif self.direction == 180 and self.y < 9:
            if not is_wall(self.x, self.y + 1) and not is_bot(self.x, self.y + 1) and not is_player(self.x, self.y + 1):
                self.y += 1
        elif self.direction == 270 and self.x > 0:
            if not is_wall(self.x - 1, self.y) and not is_bot(self.x - 1, self.y) and not is_player(self.x - 1, self.y):
                self.x -= 1
        print("position - ", self.x, self.y)
        return self

    # player move backward
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
        return self

    # player rotate anti-clockwise
    def rotate_a(self):
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.direction -= 90
        if self.direction < 0: self.direction += 360
        print(self.direction)
        return self

    # player rotate clockwise
    def rotate_d(self):
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        self.direction += 90
        if self.direction > 270: self.direction -= 360
        print(self.direction)
        return self

    # def to launch a bullet from player, starting own bullet thread
    def shoot(self):
        global bullet_moving, bullet
        with bullet_lock:
            if not bullet_moving:
                bullet_moving = True
                pos_x, pos_y = step_direction(self)
                # bullet.direction = self.direction
                if not is_wall(pos_x, pos_y):
                    bullet = Bullet(pos_x, pos_y, bullet_image, self.direction)
                threading.Thread(target=self._move_bullet, args=(bullet,), daemon=True).start()

    # to make bullet moving, checking if collide
    def _move_bullet(self, bullet):
        global bullet_moving, bot
        while bullet_moving and not self.exit_pressed:
            time.sleep(1 / 30)
            with bullet_lock:
                if bullet.move():
                    bullet_moving = False
                    print("COLLIDE!!!!")
                    if is_bot(bullet.x, bullet.y):
                        bot.hp -= 1
                        if bot.hp == 0:
                            print("THE BOT WAS KILLED")
                            print("-----------END OF THE GAME--------------")
                            Player.exit_pressed = True
                            bullet_moving = False
                            print(Player.exit_pressed)
                            print(threading.enumerate())
                            print(threading.main_thread())
                            break
                        break
        bullet_moving = False


class Bot(Player):
    # describing how bot is moving
    # spiral movement towards player
    hp = 3

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

    def move_towards_target(self):
        global player
        while [self.x, self.y] != [player.x, player.y] or not Player.exit_pressed:
            # Calculate relative position
            # delta - distance between bot and player
            delta_x = self.x - player.x
            delta_y = self.y - player.y
            time.sleep(0.33)
            # Rotate towards the target
            self.rotate_towards_target(delta_x, delta_y)
            # Move towards the target
            x_mem = self.x
            y_mem = self.y
            variety = random.randint(0, 10)
            if variety <= 3:
                bot.shoot()
            if Player.exit_pressed:
                break
            self.forward()
            # if bot is stuck, it will try to rotate and move
            if self.x == x_mem and self.y == y_mem:
                self.rotate_d()
                self.forward()

    def rotate_towards_target(self, delta_x, delta_y):
        angle_to_target = self.calculate_angle(delta_x, delta_y)

        while self.direction != angle_to_target:
            # Rotate 90 degrees to the right or left
            if self.direction < angle_to_target:
                self.rotate_d()
            else:
                self.rotate_a()

    # Function to calculate the angle of rotation
    def calculate_angle(self, delta_x, delta_y):
        # Calculate the angle (in degrees) from (1, 0) to (delta_x, delta_y)
        angle = math.degrees(math.atan2(delta_y, delta_x))
        # Ensure the angle is between 0 and 360
        if angle < 0:
            angle += 360
        if 0 <= angle < 90:
            angle = 0
        elif 90 <= angle < 180:
            angle = 90
        elif 180 <= angle < 270:
            angle = 180
        elif 270 <= angle <= 360:
            angle = 270
        return angle

    #set bot_bullet as moving object
    def bot_shoot(self):
        global bot_bullet_moving, bot_bullet
        print("BOT IS SHOOTING")
        with bot_bullet_lock:
            if not bot_bullet_moving:
                bot_bullet_moving = True
                bot_bullet = Bullet(self.x, self.y, bullet_image, self.direction)
                print("start position of bot bullet is - ", bot_bullet.x, bot_bullet.y, bot_bullet.direction)
                threading.Thread(target=self._bot_move_bullet, args=(bot_bullet,), daemon=True).start()

    # to move bot_bullet, checking if collide
    def _bot_move_bullet(self, bot_bullet):
        global bot_bullet_moving, player
        while bot_bullet_moving and not player.exit_pressed:
            bot_bullet.move()
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
        self.image = image
        self.direction = direction
        self.speed = speed

    # function of processing the bullet moving

    def move(self):
        collide = False
        if self.direction == 0:
            collide = self.move_0()
        elif self.direction == 90:
            collide = self.move_90()
        elif self.direction == 180:
            collide = self.move_180()
        elif self.direction == 270:
            collide = self.move_270()
        return collide


    def move_0(self):
        collide = False
        if not is_wall(self.x, self.y - 1) and not is_bot(self.x, self.y - 1) and self.y > 0:
            self.y -= self.speed
            time.sleep(1 / 30)
        else:
            collide = True
        return collide

    def move_90(self):
        collide = False
        if not is_wall(self.x + 1, self.y) and not is_bot(self.x + 1, self.y) and self.x <= 9:
            self.x += self.speed
            time.sleep(1 / 30)
        else:
            collide = True
        return collide


    def move_180(self):
        collide = False
        if not is_wall(self.x, self.y + 1) and not is_bot(self.x, self.y + 1) and self.y <= 9:

            self.y += self.speed
            time.sleep(1 / 30)
        else:
            collide = True
        return collide

    def move_270(self):
        collide = False
        if not is_wall(self.x - 1, self.y) and not is_bot(self.x - 1, self.y) and self.x > 0:
            self.x -= self.speed
            time.sleep(1 / 30)
        else:
            collide = True
        return collide

# auto-renewable of a screen every 300ms
def screen_renew(background, player, bot):
    global bullet, bot_bullet
    while not Player.exit_pressed:
        draw_player(background, player, bullet, bot)
        # Update the bullet's position if it's moving
        if bullet_moving:
            bullet.move()
        if bot_bullet_moving:
            bot_bullet.move()
        key = cv2.waitKey(10)
        time.sleep(1 / 60)
        if key == 27 or player.exit_pressed:
            cv2.destroyAllWindows()
            break

# one frame drawing
# creating an image of every object and putting it in the frame
def draw_player(background, player, bullet, bot):
    """draws the player image on the screen"""
    frame = background.copy()
    xpos, ypos = player.x * TILE_SIZE, player.y * TILE_SIZE
    frame[ypos: ypos + TILE_SIZE, xpos: xpos + TILE_SIZE] = player.image
    bot_x, bot_y = bot.x * TILE_SIZE, bot.y * TILE_SIZE
    frame[bot_y: bot_y + TILE_SIZE, bot_x: bot_x + TILE_SIZE] = bot_image
    for wall in walls:
        image_link(wall.x, wall.y, wall_image, frame)
    if bullet_moving:
        image_link(bullet.x, bullet.y, bullet.image, frame)
    if bot_bullet_moving:
        image_link(bot_bullet.x, bot_bullet.y, bullet.image, frame)
    cv2.imshow("frame", frame)
    cv2.waitKey(10)

# creating a single object in the frame
def image_link(x, y, image, frame):
    xpos, ypos = int(x * TILE_SIZE), int(y * TILE_SIZE)
    try:
        frame[ypos: ypos + TILE_SIZE, xpos: xpos + TILE_SIZE] = image
    except ValueError:
        raise MyException

# single screen drawing with static po
def double_size(img):
    """returns an image twice as big"""
    return np.kron(img, np.ones((2, 2, 1), dtype=img.dtype))

# checking function is position a wall
def is_wall(x, y):
    flag = False
    if not 0 <= x <= 9: flag = True
    if not 0 <= y <= 9: flag = True
    for wall in walls:
        if int(wall.x) == int(x) and int(wall.y) == int(y):
            flag = True
            break
    return flag

# checking function is position a bot
def is_bot(x, y):
    global bot
    if bot.x - 0.5 <= x <= bot.x + 0.5:
        if bot.y - 0.5 <= y <= bot.y + 0.5:
            return True

# checking function is position a player
def is_player(x, y):
    global player
    if player.x - 0.5 <= x <= player.x + 0.5:
        if player.y - 0.5 <= y <= player.y + 0.5:
            return True



# function of prediction next step based on direction
"""Currently not used"""
def step_direction(player):
    step = [] # [x, y]
    if player.direction == 0:
        step = [player.x, player.y - 1]
    elif player.direction == 90:
        step = [player.x + 1, player.y]
    elif player.direction == 180:
        step = [player.x, player.y + 1]
    elif player.direction == 270:
        step = [player.x - 1, player.y]
    return step[0], step[1]


# function of processing a keyboard input
def on_press(key):
    global player
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
        if key.char == 'w' or key.char == 'ц': player.forward()
        if key.char == 's' or key.char == 'ы': player.backward()
        if key.char == 'a' or key.char == 'ф': player.rotate_a()
        if key.char == 'd' or key.char == 'в': player.rotate_d()
        if key.char == 'q' or key.char == 'й':
            Player.exit_pressed = True
            return False
        if key.char == 'e' or key.char == 'у':
            player.shoot()
            return bullet
        if key == kb.Key.esc:
            # Stop listener
            Player.exit_pressed = True
            return False
    except AttributeError:
        if key == kb.Key.esc:
            Player.exit_pressed = True
            return False


def on_release(key):
    if key == kb.Key.esc:
        # Stop listener
        Player.exit_pressed = True
        return False
    if key.char == 'q' or key.char == 'й':
        Player.exit_pressed = True
        return False

# function of starting a game, starting threads
def start():
    thread_screen = threading.Thread(target=screen_renew, args=(background, player, bot), daemon=True)
    thread_bot = threading.Thread(target=bot.move_towards_target, daemon=True)
    thread_bot.start()
    thread_screen.start()
    with kb.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
    thread_screen.join()
    thread_bot.join()
    if Player.exit_pressed:
        kb.Listener = kb.Listener.stop

    #cv2.destroyAllWindows()

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
player = Player(xpos, ypos, 0, player_image)
# create a bot object
bot = Bot(1, 1, 0, bot_image)

# create a walls object
#  wall_show()

# creating bullets
bullet = Bullet(0, 0, bullet_image, 0)
bot_bullet = Bullet(0, 0, bullet_image, 0)

exit_pressed = False
bullet_moving = False
bot_bullet_moving = False
print(Player.exit_pressed)
#print("WALLS - ", walls)