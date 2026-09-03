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
Our configuration files can be used to choose the highscore file name, the number of lives, points earned, the game time and level specific settings such as a seed and the number of pacgums. There are default values if none or wrong ones are given, using pydantic.

## Highscore
Our highscore system is pretty straight forward, the new score is compared to already existing scores and sorted, then the first 10 scores will be shown. If a player name already exists, only the highest score will be kept, in order to not have doubles.

## Maze Generation
We use the A-Maze-ing package to create a random maze, simply calling the program by giving it the size we want for our maze

## Implementation
technical summary of your implementation

## General Software Architecture
high-level overview of the software architecture (modules, classes, and their relationships)

## Project Management
We established a 4-week plan, with milestones for each week, and agreed on who would do what.
<!-- brief overview of how you managed the activity and a link to the dedicated project management directory -->
