*This activity has been created as part of the 42 curriculum by lulaurent and aupeuget*

# Pacman

## Description
This activity consists in the creation of a Pac-Man game in Python using OOP.
The game must use an external maze generator package, and a configuration file to configure the game.

## Instruction
For compilation, use command `make install` that will create a virtual environment and download any needed module used by our program, then `make run` to run the program. To delete pycache and mypy cache, use `make clean`, to delete all files except for the code, use `make fclean`. To check if the file has flake8/mypy errors, use `make lint` or `make lint-strict` to use flag --strict for mypy.  

## Resources / AI use
https://pydantic.dev/docs/validation/latest/concepts/fields/
https://coderslegacy.com/python/python-pygame-tutorial/
https://pacmancode.com/
https://www.geeksforgeeks.org/python/pygame-drawing-objects-and-shapes/
https://stackoverflow.com/questions/73328115/pacman-ghost-movement

AI was used to debug and for testing.

## Configuration
Our configuration file can be used to choose the highscore file name, the number of lives, the amount of points earned, the game duration and level specific settings such as a seed and the number of pacgums. There are default values if none or wrong ones are given. We use pydantic to parse this Json configuration file.

## Highscore
Our highscore system is pretty straight forward, the new score is compared to already existing scores and sorted, then the first 10 scores will be shown. If a player name already exists, only the highest score will be kept, in order to not have doubles.

## Maze Generation
We use the A-Maze-ing package to create a random maze, simply calling the program by giving it the size we want for our maze.

## Implementation
| Step     | Description |
|:-------- |:--------:|
| Parsing     | Parsing of the JSON configuration file. |
| Game init    | Initialization of the GameController class using the parsing of the configuration file and creation of the maze with the MazeGenerator module (the first level will have a seed, the next levels will be random). |
| Main menu     | Start the main menu where the player will be able to choose between starting the game, checking the instructions, checking the leaderboard or exiting the game. |
| Launching the game | PacWoman moves depending on the player, gets eaten by ghosts if they touch her, unless she ate a super pacgum, in this case, a timer will be set. The number of lives are decided in the configuration file. The ghosts have 4 different algorithms based on a BFS algorithm, they have 3 different state: chase (where they use their algorithm), scared (when PacWoman can eat them, they will move randomly), scatter (every 40 seconds they head to their spawn location for a 6 seconds). |
| Pausing the game | When the game is paused, the timers will also be paused and the ghosts and PacWoman will stop moving. The player will be able to choose betweem resuming the game, restarting, going back to the main menu or exiting. |
| Dying | When the player dies, PacWoman and the ghosts spawn back to their initial spawning location (PacWoman in the middle and the ghosts at each corner of the maze). If the player doesn't have anymore lives, the game over menu will show where the player can enter their name to save their score, view the leaderboard, restart from beginning, quit the game, or check instructions for cheat codes. |
| Winning | When the player wins a level, they will have the game over menu with one more option than when dying, to be able to advance to the next level. If the player has won the game, they will have the same menu with the possibility to restart or check the leaderboard to see if they are in it. |
| Restarting the game | When the game is restarted, all variables are set back to their default values, the eaten PacGums reappear and the Ghosts and PacWoman are moved back to their spawning locations.  |

## General Software Architecture
We have divided the project in several files that all have their use to make it cleaner and easier to make changes.
The game_controller file is our main file, it orchestrates the whole game: from creation of the maze, handling the events and the menus to moving the ghosts...

### Modules
We are using Pygame which allows us to have a clean interface in a dedicated window, handling events, themes and sprites. We also use Pygame_menu that allows us to create our user friendly menus.  
For the parser we use Pydantic to parse the data from the configuration file cleanly.

### Classes
| Class     | Use |
|:-------- |:--------:|
| BaseModel | Used to to cleanly handle any error in the configuration file and have default values if needed. |
| GameController, PacWoman, Ghosts | GameController handles the game from start to finish, using our PacWoman, and Ghosts classes (with dedicated subclasses for each ghost) which are responsible for the sprites and the movements of the characters. |
| PacGums | Displays the pacgums in the maze and removes them when PacWoman eats them, add the points to the score and allows PacWoman to eat the Ghosts for a given period of time. |

## Project Management
We established a 4-week plan, with milestones for each week, and agreed on who would do what. We would communicate often on how the project was going and gave each other daily updates on our progress. 

> Link to project management directory
<!-- brief overview of how you managed the activity and a link to the dedicated project management directory -->
