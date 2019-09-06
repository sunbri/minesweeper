# Minesweeper Solver
Uses a deep neural network through Tensorflow to predict whether or not a given Minesweeper block will be a mine or not. [Here](https://www.youtube.com/watch?v=a2z3GWWXZuc) is a video of the trained model on a test game of Minesweeper. The accuracy is at the bottom and in the video, you can see a green soutline Here's a quick description of the files:

| File              | Description                                  |
| ------------------|----------------------------------------------|
| model.py          | Structure and logic of the deep net          |
| albert.py         | GUI and Minesweeper logic                    |
| mine_data.py      | Collects training data via simulated "games" |
| pickle_combine.py | Cleans training data                         |

All of the images and some files containing pickle'd lists or saved models are omitted for the sake of space and cleanliness. A little write-up about the process of collecting training data and finding the best structure for the deep net is below.

## General Algorithm Remarks
For eachs square that needs to be predicted, the deep net takes in a vector of 24 integers that correspond to eithe numbers, flags, blank spaces, or unclicked squares as input. These 24 integers correspond to the squares that form two rings around the square that we wish to predict (think of a 5x5 square with what we wish to predict in the middle). However, since there's no ordering for these numbers (a flag can't be "greater than" or "less than" a blank), it doesn't make sense to feed in raw data, scaled or not. To solve this problem, the first layer of the deep net is an embedded layer, which represents each possible integer input as a vector in n-dimensional space. The components of these vectors are then tuned as the network learns, and the components of the vectors are flattened and fed forward throughout the network.

The other important part of the algorithm besides the structure of the network is developing a method to select the next square to guess. In this case, the algorithm was programmed to select the square that had the most revealed squares (including flags and squares "off the edge"), as those squares are the ones that have the most revealed data around them. 

## Collecting the Training Data
Finding the best way to collect the training data was quite simple. To have the training data match what would happen in a test game, I simulated over 200 games on board sizes of approximately 10000 squares, "playing" the game like how the AI would end up playing it. That is, I chose the squares that had the highest number of neighbors, captured the squares around it as the training data, and captured the value of the square (mine or not) as the labels. Iterating this over and over again would simulate a perfect AI, and this data was used to train the neural net. 

## Tuning the Hyperparamters
In this case, an embedded neural net with two dense layers and dropout is enough to train a neural net with a validation acuracy of approximatley 95%. In the video above, the model had over a 97% accuracy on the test case, which is a little better than what would be expected. There are two hidden layers to ensure that overfitting is avoided. In this case, however, it seems like overfitting the training data wouldn't be too much of an issue since it is sampled from the same "population" as the actual test data, and there would be no invariance. 
