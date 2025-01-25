import cv2
import numpy as np
import os
from datetime import datetime

# Function to check if the current time is between 8 PM and 9 PM
def is_valid_time():
    current_time = datetime.now().time()
    start_time = datetime.strptime("20:00:00", "%H:%M:%S").time()  # 8:00 PM
    end_time = datetime.strptime("21:00:00", "%H:%M:%S").time()    # 9:00 PM
    
    # Check if the current time is within the specified range
    if start_time <= current_time <= end_time:
        return True
    return False

# Function to create a collage
def create_collage(image_paths, collage_width, collage_height):
    # Read the images and store them in a list
    images = [cv2.imread(img_path) for img_path in image_paths]
    
    # Resize images to a standard size
    resized_images = [cv2.resize(img, (collage_width, collage_height)) for img in images]

    # Create a blank canvas for the collage
    collage = np.zeros((collage_height * 2, collage_width * 2, 3), dtype=np.uint8)

    # Place images on the canvas in a 2x2 grid
    for i, img in enumerate(resized_images):
        row = i // 2
        col = i % 2
        collage[row * collage_height:(row + 1) * collage_height, col * collage_width:(col + 1) * collage_width] = img
    
    return collage

# Main function
def main():
    # Ensure the program only runs between 8 PM and 9 PM
    if not is_valid_time():
        print("The program can only run between 8 PM and 9 PM.")
        return
    
    # Path to your images directory (make sure images are in this folder)
    image_dir = 'C:/Users/user-307E7B3400/Downloads/drive-download-20250117T123348Z-001'  # Replace with the path to your images folder
    image_paths = [os.path.join(image_dir, fname) for fname in os.listdir(image_dir) if fname.endswith('.jpg') or fname.endswith('.png')]
    
    # Check if there are enough images for the collage
    if len(image_paths) < 4:
        print("Not enough images to create a collage. Please add at least 4 images.")
        return
    
    # Define the width and height of each image in the collage
    collage_width = 300  # Width of each image in pixels
    collage_height = 300  # Height of each image in pixels

    # Create the collage using the first 4 images
    collage = create_collage(image_paths[:4], collage_width, collage_height)  # Only use the first 4 images
    
    # Display the collage
    cv2.imshow('Collage', collage)
    
    # Save the collage as an image file
    cv2.imwrite('collage_output.jpg', collage)

    # Wait until a key is pressed to close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
