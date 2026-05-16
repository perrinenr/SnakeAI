# AI Snake with A* Algorithm

This project is an AI-based Snake project developed in Python.  
It is not only a simple Snake game, because the snake can move automatically using the A* pathfinding algorithm.

## Project Idea

The goal of this project is to create a Snake AI that can find the best path to reach the food.  
Instead of controlling the snake manually, the program uses artificial intelligence to decide the next movement.

The A* algorithm is used to search for the shortest and safest path between the snake's head and the food.

## Features

- Snake game environment developed in Python
- Automatic snake movement using AI
- A* pathfinding algorithm
- Collision detection with walls and the snake body
- Score system
- Configurable game settings
- Clean code structure using multiple Python files

## Technologies Used

- Python
- Pygame
- A* Algorithm
- Artificial Intelligence logic

## Files Description

- `main.py`: starts the program and controls the main loop
- `snake.py`: contains the snake logic, movement, and collision handling
- `astar.py`: contains the A* pathfinding algorithm
- `config.py`: contains the game settings such as window size, colors, and speed
- `README.md`: project documentation
- `.gitignore`: ignores unnecessary files

## How to Run the Project

1. Install Python.
2. Install Pygame:

```bash
pip install pygame
