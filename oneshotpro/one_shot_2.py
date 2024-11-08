# -*- coding: utf-8 -*-
"""One-Shot 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12JOadP8kT63A4m2c6k0SBlIoiwBS4upA
"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_and_preprocess_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load the image at path: {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (500, 500))
        image = image.astype('float32') / 255.0  # Normalize the image
        return image
    except Exception as e:
        raise ValueError(f"Error occurred while processing the image: {e}")

def calculate_similarity(image1, image2):
    feature1 = np.mean(image1, axis=(0, 1))
    feature2 = np.mean(image2, axis=(0, 1))
    similarity = np.linalg.norm(feature1 - feature2)
    return similarity

def predict_spex(image_path, anchor_image_path, threshold=0.8):
    anchor_image = load_and_preprocess_image(anchor_image_path)
    test_image = load_and_preprocess_image(image_path)

    similarity = calculate_similarity(anchor_image, test_image)

    if similarity >= threshold:
        prediction = "spex"
    else:
        prediction = "no_spex"

    accuracy = 1 - abs(similarity - threshold)  # Calculate the accuracy based on the similarity

    return prediction, accuracy, test_image

# Replace the image_path and anchor_image_path with the paths to your test image and anchor image, respectively
test_image_path = '/content/drive/MyDrive/spex/test/withspex3.jpeg'
anchor_image_path = '/content/drive/MyDrive/spex/train/spex/image5.jpeg'

# Replace the threshold value as desired
threshold = 0.249
# Predict if the person is wearing spectacles or not and calculate accuracy
predicted_class, accuracy, test_image = predict_spex(test_image_path, anchor_image_path, threshold)

# Resize the image to the correct size
resized_test_image = cv2.resize(test_image, (500, 500))

# Calculate the size of the image
image_size = resized_test_image.shape[:2]

# Display the resized image and prediction
plt.figure(figsize=(3, 3))  # Set the figure size as a square (6x6 inches)
plt.imshow(resized_test_image)
plt.axis('off')
plt.title(f"The person is {'wearing spectacles' if predicted_class == 'spex' else 'not wearing spectacles'}. "
          f"Accuracy: {accuracy:.2%}")
plt.show()

