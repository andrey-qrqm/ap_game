Welcome to my game repository!
This was the task from course in my University, so here we are. 
For myself, the goal of this project was to make first contact with multithreading in Python. So, here I tried to implement mechanics of multithreading.
As an inspiration I took browser games from my childhood called 'Tanks'. They had thousands of variations and you can easily find ones still online and try them too.

So, what had I done here? My game for today is in the state of MVP, so It is a 2D shooter with Top point of view. As a player you are controlling one of the tanks (green one). And your task is to shoot down
enemy (yellow) tank as fast as you can. The enemy heath bar equals 3, so for the win you should make a successfull shot 3 times. The bot will move towards you, but it will try to go out from your shooting line.
Bot will as well try to frighten you with their own shots, but for today your tank is too strong to get some affects from this bullets. The terrain and walls will generate automatically in the beginning of
every game. 

To start the game you will need to download requirements.txt with libraries. 
For example you can do it with next line in terminal:

py -m pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt 

The next step is to run launcher.py and you are free to play!

py .\launcher.py

*** py can be modyfied to python3 or python based on your system

How to play:
WASD - moving and rotation
E - shooting or play again
Q - quit the game

Have fun!

In my game code I have implemented pieces of code from my university professor K. Rother game. You can find his approach here:  https://github.com/krother/ams_dungeon_explorer 
Some visual and sounds were taken from https://opengameart.org, others (tanks and bullet models) were created by my friend Fedor.

