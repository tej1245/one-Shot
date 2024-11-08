# -*- coding: utf-8 -*-
"""One-Shot 1 .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1phHBN9Q5J7kTcvQy7CNaSWulD-kXOtiV
"""

import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, Flatten, Dense, Lambda
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import binary_crossentropy
import matplotlib.pyplot as plt

def load_and_preprocess_images(directory):
    images = []
    for file in os.listdir(directory):
        if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
            image_path = os.path.join(directory, file)
            try:
                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (224, 224))
                images.append(image)
            except Exception as e:
                print(f"Error occurred while processing image {image_path}: {e}")

    if not images:
        raise ValueError("No images found in the specified directory.")

    return np.array(images)

def create_siamese_network(input_shape):
    input_left = Input(input_shape)
    input_right = Input(input_shape)

    model = Conv2D(32, (3, 3), activation='relu')
    output_left = model(input_left)
    output_right = model(input_right)

    # Calculate the Euclidean distance between the two outputs
    distance = Lambda(lambda x: tf.abs(x[0] - x[1]))([output_left, output_right])
    output = Dense(1, activation='sigmoid')(Flatten()(distance))

    siamese_network = Model(inputs=[input_left, input_right], outputs=output)
    return siamese_network

def train_siamese_network(train_directory):
    # Load the training data
    class_directories = [os.path.join(train_directory, 'no_spex'), os.path.join(train_directory, 'spex')]
    images_per_class = []
    for class_dir in class_directories:
        images = load_and_preprocess_images(class_dir)
        images_per_class.append(images)

    # Create pairs of anchor and comparison images
    pairs = []
    labels = []
    for i in range(len(class_directories)):
        for j in range(len(images_per_class[i])):
            for k in range(j+1, len(images_per_class[i])):
                pairs.append([images_per_class[i][j], images_per_class[i][k]])
                labels.append(1)  # 1 indicates images from the same class

            for l in range(i+1, len(class_directories)):
                for m in range(len(images_per_class[l])):
                    pairs.append([images_per_class[i][j], images_per_class[l][m]])
                    labels.append(0)  # 0 indicates images from different classes

    pairs = np.array(pairs)
    labels = np.array(labels)

    # Shuffle the data
    indices = np.arange(len(pairs))
    np.random.shuffle(indices)
    pairs = pairs[indices]
    labels = labels[indices]

    # Split the data into training and validation sets
    split_idx = int(0.8 * len(pairs))
    train_pairs, val_pairs = pairs[:split_idx], pairs[split_idx:]
    train_labels, val_labels = labels[:split_idx], labels[split_idx:]

    # Create the siamese network
    input_shape = train_pairs.shape[2:]
    siamese_network = create_siamese_network(input_shape)
    siamese_network.compile(optimizer=Adam(), loss=binary_crossentropy, metrics=['accuracy'])

    # Train the siamese network
    siamese_network.fit([train_pairs[:, 0], train_pairs[:, 1]], train_labels,
                        validation_data=([val_pairs[:, 0], val_pairs[:, 1]], val_labels),
                        epochs=10, batch_size=32)

    return siamese_network

def predict_spex(test_image_path, siamese_network, threshold=0.5):
    try:
        # Preprocess the test image
        test_image = cv2.imread(test_image_path)
        if test_image is None:
            raise ValueError(f"Failed to load the test image at path: {test_image_path}")
        test_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        test_image = cv2.resize(test_image, (224, 224))
        test_image = np.expand_dims(test_image, axis=0)

        # Redefine class_directories in the local scope
        class_directories = [os.path.join(train_directory, 'no_spex'), os.path.join(train_directory, 'spex')]

        # Create pairs with the test image and the training images
        pairs = []
        for class_dir in class_directories:
            images = load_and_preprocess_images(class_dir)
            for image in images:
                pairs.append([test_image, image])

        # Create a ragged tensor from the pairs
        pairs = tf.ragged.constant(pairs)

        # Make predictions using the siamese network
        predictions = siamese_network.predict([pairs[:, 0], pairs[:, 1]])
        predictions = predictions.numpy()  # Convert to a NumPy array
        mean_prediction = np.mean(predictions)

        if mean_prediction >= threshold:
            return "spex"
        else:
            return "no_spex"

    except Exception as e:
        print(f"Error occurred while predicting spex: {e}")
        return None




# Replace the paths with the paths to your train directory and test image
train_directory = '/content/drive/MyDrive/spex/train'
test_image_path = '/content/drive/MyDrive/spex/train/spex/image1.jpeg'

# Train the siamese network
siamese_network = train_siamese_network(train_directory)

# Predict the class of the test image
predicted_class = predict_spex(test_image_path, siamese_network)

# Display the test image with the predicted class
test_image = cv2.imread(test_image_path)
test_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
plt.imshow(test_image)
plt.title(f"The person is {'wearing spex' if predicted_class == 'spex' else 'not wearing spex'}.")
plt.axis('off')
plt.show()
