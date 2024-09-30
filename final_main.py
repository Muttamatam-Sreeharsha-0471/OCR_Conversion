import os
import easyocr
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import cv2
from matplotlib import pyplot as plt
import numpy as np
from final_filter import *  # Assuming you have utility functions here

# Initialize EasyOCR Model (do it once to avoid loading the model multiple times)
reader = easyocr.Reader(['en'])

# Function to run EasyOCR on an image


def easyocr_model(image):
    """
    Perform OCR on an image using EasyOCR.

    Parameters:
    image (numpy array): The pre-processed image on which OCR will be performed.

    Returns:
    str: Extracted text from the image.
    """
    result = reader.readtext(image)
    # Join all extracted text segments
    text = ' '.join([item[1] for item in result])
    return text

# Convert image to grayscale


def grayscale(image):
    """
    Convert the input image to grayscale.

    Parameters:
    image (numpy array): Original image in BGR format.

    Returns:
    numpy array: Grayscale image.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Function to download and load image from a URL


def load_image_from_url(image_url):
    """
    Download an image from the given URL and load it into memory using PIL.

    Parameters:
    image_url (str): URL of the image to download.

    Returns:
    PIL.Image or None: Returns the image if successful, else None.
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            print(f"Failed to download image from {image_url}")
            return None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Function to check if inversion is needed for better OCR accuracy


def inversion_check(img):
    """
    Check if the image has a dark background and invert it if necessary.

    Parameters:
    img (numpy array): Grayscale image.

    Returns:
    numpy array: The potentially inverted grayscale image.
    """
    gray_image = grayscale(img)
    mean_intensity = np.mean(gray_image)
    print(f"Mean intensity: {mean_intensity}")

    # If mean intensity is below threshold, the background is considered dark, so invert the image
    if mean_intensity < 127:  # Threshold at midpoint (127) between 0 and 255
        gray_image = cv2.bitwise_not(gray_image)
    return gray_image

# Function to sharpen the image for better OCR accuracy


def sharpen_image(gray_image):
    """
    Apply a sharpening filter to the image.

    Parameters:
    gray_image (numpy array): Grayscale image to be sharpened.

    Returns:
    numpy array: Sharpened image.
    """
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])  # Sharpening kernel
    return cv2.filter2D(gray_image, -1, kernel)


# Load the dataset from a CSV file
input_csv = 'C:/Users/Shubham/Desktop/AML/main/exp.csv'
output_csv = 'output_easyocr.csv'

# Read input data
data = pd.read_csv(input_csv)

# Initialize results list and set batch size for periodic saving
results = []
batch_size = 5  # Save results to CSV every 5 images

# Main loop to process each image
for _, row in data.iterrows():
    index = row['index']
    image_link = row['image_link']
    entity_name = row['entity_name']

    print(f"Processing Image: {image_link}")

    # Load image from URL
    image = load_image_from_url(image_link)

    if image:
        try:
            # Convert PIL image to a numpy array (OpenCV format)
            image_np = np.array(image)

            # Pre-process image: Grayscale, check for inversion, then sharpen
            grayscale_image = inversion_check(image_np)
            sharpened_image = sharpen_image(grayscale_image)

            # Perform OCR to extract text
            extracted_text = easyocr_model(sharpened_image)
        except Exception as e:
            # In case of an error, save the error message
            extracted_text = f"Error: {e}"
    else:
        # Handle case where image couldn't be loaded
        extracted_text = "Image not available"

    # Process extracted text to get numerical values and units
    extract, num, units = convert_to_full_unit(extracted_text)
    categorized_values = categorize_values(num, units)
    final_val = get_entity_value(entity_name, categorized_values)

    # Store results in a list
    results.append({
        'index': index,
        'prediction': final_val
    })

    print(f'Index: {index}, Entity Value: {entity_name}, Value: {final_val}')

    # Save results every batch_size iterations or at the last iteration
    if (index + 1) % batch_size == 0 or index == len(data) - 1:
        output_df = pd.DataFrame(results)

        # Append to CSV if it exists, otherwise create it
        if not os.path.isfile(output_csv):
            output_df.to_csv(output_csv, index=False,
                             columns=['index', 'prediction'])
        else:
            output_df.to_csv(output_csv, mode='a', header=False,
                             index=False, columns=['index', 'prediction'])

        # Clear results list after saving to CSV
        results = []

        print(f"Appended results to {output_csv}")

print(f"Results saved to {output_csv}")
