# Minesweeper Solver
Uses a deep neural network through Tensorflow to predict whether or not a given Minesweeper block will be a mine or not. [Here](https://www.youtube.com/watch?v=a2z3GWWXZuc) is a video of the trained model on a test game of Minesweeper. Here's a quick description of the files:

| File              | Description                                  |
| ------------------|----------------------------------------------|
| model.py          | Structure and logic of the deep net          |
| albert.py         | GUI and Minesweeper logic                    |
| mine_data.py      | Collects training data via simulated "games" |
| pickle_combine.py | Cleans training data                         |

All of the images and some files containing pickle'd lists or saved models are omitted for the sake of space and cleanliness.
