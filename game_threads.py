"""
Proof-of-concept: move around on a 2D grid

Install dependencies:

    pip install opencv-python
"""


### LIBRARY ARCADE
import random
import threading
import keyboard
import time
import walls_generator
import cv2
import math
import numpy as np
from pynput import keyboard as kb

bullet_lock = threading.Lock()
bot_bullet_lock = threading.Lock()
bot_image_lock = threading.Lock()


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
        print('rotate_a', self.direction, self)
        return self

    # player rotate clockwise
    def rotate_d(self):
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        self.direction += 90
        if self.direction > 270: self.direction -= 360
        print(self.direction, 'rotate_b', self)
        return self

    def step_direction(self):
        step = 1
        x, y = self.x, self.y
        if self.direction == 0:
            x = self.x
            y = self.y - step
        elif self.direction == 90:
            x = self.x + step
            y = self.y
        elif self.direction == 180:
            x = self.x
            y = self.y + step
        elif self.direction == 270:
            x = self.x - step
            y = self.y
        return x, y

    # def to launch a bullet from player, starting own bullet thread
    def shoot(self):
        global bullet_moving, bullet
        with bullet_lock:
            print("Player bullet exist")
            if not bullet_moving:
                bullet_moving = True
                pos_x, pos_y = self.step_direction()
                # bullet.direction = self.direction
                if not is_wall(pos_x, pos_y):
                    bullet = Bullet(pos_x, pos_y, bullet_image, self.direction, "player")
                bullet_thread = threading.Thread(target=self._move_bullet, args=(bullet,), daemon=True)
                bullet_thread.start()



    # to make bullet moving, checking if collide
    def _move_bullet(self, bullet):
        global bullet_moving
        while bullet_moving and not Player.exit_pressed and Bot.hp > 0:
            print("move_bullet is running")
            time.sleep(1 / 30)
            print("bullet is moving")
            with bullet_lock:
                if bullet.move():
                    bullet_moving = False
                    print("COLLIDE!!!! here")
                    print("Bullet stop moving")
                    if is_bot(bullet.x, bullet.y) and bullet.shooter == "player":
                        Bot.hp -= 1
                        print("BOT HP - ", Bot.hp, "SHOOTER - ", bullet.shooter)
                        break
        bullet_moving = False


class Bot(Player):
    # Bot Health Points (how many times bullet should hit bot to it to be killed)
    hp = 3

    # describing how bot is moving
    # spiral movement towards player
    def move_towards_target(self):
        global player
        with bot_image_lock:
            while [self.x, self.y] != [player.x, player.y] or not Player.exit_pressed:
                print("Bot is moving")
                if Bot.hp <= 0:
                    Player.exit_pressed = True
                    print(threading.enumerate())
                    print("BOT hp is 0")
                    # the next line of code make me waste 8 hours of debugging, it is the only solution I have found
                    # Without it thread_screen is shutting down and program exits the cv2 window, however it didn't finish
                    # and waits for something. By pressing 'q' I am triggering proper finish and exit. If you would like to
                    # find other solution I would be happy to hear them.
                    keyboard.press('q')
                    break

                print("move_towards_target is running")
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
                    bot.bot_shoot()
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
                posx, posy = self.step_direction()
                if not is_wall(posx, posy):
                    bot_bullet = Bullet(posx, posy, bullet_image, self.direction, "bot")
                print("start position of bot bullet is - ", bot_bullet.x, bot_bullet.y, bot_bullet.direction)
                threading.Thread(target=self._bot_move_bullet, args=(bot_bullet,), daemon=True).start()

    # to move bot_bullet, checking if collide
    def _bot_move_bullet(self, bot_bullet):
        global bot_bullet_moving, player
        while bot_bullet_moving and not player.exit_pressed:
            print("move_towards_target is running")
            bot_bullet.move()
            time.sleep(1 / 30)
            with bot_bullet_lock:
                #print("bullet is moving")
                if bot_bullet.move():
                    bot_bullet_moving = False
                    #print("Bullet stop moving")
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
    speed = 0.5

    def __init__(self, x, y, image, direction, shooter):
        self.x = x
        self.y = y
        self.image = image
        self.direction = direction
        self.shooter = shooter

    # function of processing the bullet moving
    def move(self):
        collide = False

        # Check if the shooter is facing upwards (direction = 0) and not at the top edge
        if self.direction == 0 and self.y > 0:
            collide = self.move_until_True()
        # Check if the shooter is facing right (direction = 90) and not at the right edge
        elif self.direction == 90 and self.x < 9:
            collide = self.move_until_True()
        # Check if the shooter is facing downwards (direction = 180) and not at the bottom edge
        elif self.direction == 180 and self.y < 9:
            collide = self.move_until_True()
        # Check if the shooter is facing left (direction = 270) and not at the left edge
        elif self.direction == 270 and self.x > 0:
            collide = self.move_until_True()
        else:
            collide = True
        return collide

    def move_until_True(self):
        if self.direction == 0:
            self.y -= self.speed
        elif self.direction == 90:
            self.x += self.speed
        elif self.direction == 180:
            self.y += self.speed
        elif self.direction == 270:
            self.x -= self.speed

            # Check for collisions with walls or bots
        if self.check_collision():
            return True

            # Check if the next step is outside the grid, stop and return true
        if not (0 <= self.x <= 9 and 0 <= self.y <= 9):
            return True

        time.sleep(1 / 30)
        return False

    def check_collision(self):
        # Check for collisions with walls or bots at the new position
        if is_wall(self.x, self.y) or is_bot(self.x, self.y):
            print("COLLIDE!!!!")
            return True
        return False

# auto-renewable of a screen every 300ms
def screen_renew(background, player, bot):
    global bullet, bot_bullet
    while not Player.exit_pressed:
        #print("screen_renew")
        draw_player(background, player, bullet, bot)
        # Update the bullet's position if it's moving

# one frame drawing
# creating an image of every object and putting it in the frame
def draw_player(background, player, bullet, bot):
    """draws the player image on the screen"""
    frame = background.copy()
    xpos, ypos = player.x * TILE_SIZE, player.y * TILE_SIZE
    frame[ypos: ypos + TILE_SIZE, xpos: xpos + TILE_SIZE] = player.image
    bot_x, bot_y = bot.x * TILE_SIZE, bot.y * TILE_SIZE
    frame[bot_y: bot_y + TILE_SIZE, bot_x: bot_x + TILE_SIZE] = bot.image
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
    print("on_press....")
    try:
        if Bot.hp == 0:
            Player.exit_pressed = True
            return False
        print('alphanumeric key {0} pressed'.format(key.char))
        if key.char == 'w' or key.char == 'ц': player.forward()
        if key.char == 's' or key.char == 'ы': player.backward()
        if key.char == 'a' or key.char == 'ф': player.rotate_a()
        if key.char == 'd' or key.char == 'в': player.rotate_d()
        if key.char == 'q' or key.char == 'й':
            print("Exiting the game")
            Player.exit_pressed = True
            print(threading.enumerate())
            return False
        if key.char == 'e' or key.char == 'у':
            player.shoot()
            return bullet
        if key == kb.Key.esc:
            # Stop listener
            print("Exiting the game")
            Player.exit_pressed = True
            return False

    except AttributeError:
        if key == kb.Key.esc:
            print("Exiting the game")
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
    global player, bot, bullet, bot_bullet, bullet_moving, bot_bullet_moving

    def cleanup():
        print("Exiting the game...")
        Player.exit_pressed = True
        cv2.destroyAllWindows()

    try:
        thread_screen = threading.Thread(target=screen_renew, args=(background, player, bot), daemon=True)
        with bot_image_lock:
            thread_bot = threading.Thread(target=bot.move_towards_target, daemon=True)
            thread_bot.start()
        print("thread_bot started")
        thread_screen.start()
        print("thread_screen started")

        with kb.Listener(on_press=on_press, on_release=on_release) as listener:
            print("thread Listener started")
            listener.join()  # Wait for the listener thread to finish
            print("thread Listener joined")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        cleanup()

    print("All threads terminated.")



def start_2():
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
    print("All threads terminated")
    print(threading.enumerate())
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
bot_image = double_size(cv2.imread("yellow-boba.png"))
bot_image = cv2.rotate(bot_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
bot_image = cv2.rotate(bot_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
player_image = double_size(cv2.imread("green-booba.png"))
player_image = cv2.rotate(player_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
player_image = cv2.rotate(player_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
wall_image = double_size(cv2.imread("tiles/wall.png"))
bullet_image = double_size(cv2.imread("Bullet.png"))

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
#wall_show()

# creating bullets
bullet = Bullet(0, 0, bullet_image, 0, "player")
bot_bullet = Bullet(0, 0, bullet_image, 0, "bot")

exit_pressed = False
bullet_moving = False
bot_bullet_moving = False
print(Player.exit_pressed)
#print("WALLS - ", walls)