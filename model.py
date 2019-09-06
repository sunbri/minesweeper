# Basic interpreter changes: 
# absolute_import looks for absolute packages first, not the ones in current director
# division does float division by default
# print_function makes print a function, probably works already
# unicode_literals allows unicode strings
from __future__ import absolute_import, division, print_function, unicode_literals

# Tensorflow imports
import tensorflow as tf
from tensorflow import keras

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt
import pickle

print(tf.__version__)

# Get the data and labels and split them
train_data = pickle.load(open("joint_d.p", "rb"))

# Labels come in the form of numbers, labeled 0 for flag or 1 for click
train_labels = pickle.load(open("joint_l.p", "rb"))

# Create the model
#
# In this case, we use embedding to associate each number with a vector in a vector space
# The net will learn the positions of these vectors over time, and use that to predict the
# outcome of data it is fed
#
# The GAP layer performs dimensionality reduction to avoid overfitting - it returns a 16 
# sized vector which is the result of averaging the value in each dimension. 
#
# We then connect another dense layer and an output layer 
# We go for a modest number of hidden layers to ensure that the model is not too 
# computationally complex and also to prevent overfitting of the training data
model = keras.Sequential()

# There are 10 possible inputs
model.add(keras.layers.Embedding(11, 16, input_length=24))
model.add(keras.layers.Flatten())
model.add(keras.layers.Dense(16, activation=tf.nn.relu))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Dense(16, activation=tf.nn.relu))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

# Compilation of the model
#
# This is the same adam optimizer that was used as before - juiced up stochastic gradient
# descent
#
# The loss function is binary_crossentropy, which is used since from the logistic regression
# we are outputting a probability, where the distance is really measured in logits
#
# The metrics function shows that we are evaluating by accuracy
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['acc'])

# Create the validation set which is used to evaluate the model during training
x_val = train_data[:10000]
partial_x_train = train_data[10000:]

y_val = train_labels[:10000]
partial_y_train = train_labels[10000:]

# Train the model
model.fit(partial_x_train,
          partial_y_train,
          epochs=40,
          batch_size=512,
          validation_data=(x_val, y_val),
          verbose=1)

# Serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)

# Save weights
model.save_weights("model.h5")
print("Saved model to disk")
