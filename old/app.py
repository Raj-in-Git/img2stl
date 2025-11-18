import cv2
import numpy as np
import svgwrite
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

def image_to_svg_silhouette(image_path, svg_path, threshold=128):
    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Threshold to binary image (silhouette)
    _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours (external only)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create SVG drawing
    height, width = binary.shape
    dwg = svgwrite.Drawing(svg_path, size=(width, height))
    
    # Add paths for each contour
    for contour in contours:
        points = [(point[0][0], point[0][1]) for point in contour]
        # Create SVG path string
        path_data = "M " + " L ".join(f"{x},{y}" for x, y in points) + " Z"
        dwg.add(dwg.path(d=path_data, fill='black'))
    
    dwg.save()
    print(f"SVG saved to {svg_path}")







def show_threshold(image_path, threshold):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY_INV)
    plt.imshow(binary, cmap='gray')
    plt.title(f"Threshold = {threshold}")
    plt.axis('off')
    plt.show()

# Test different thresholds
def plot_img(image_path):
    for t in [50, 100, 128, 150, 180]:
        show_threshold(image_path, t)




# with adaptive thresholding


def image_to_svg_silhouette_adaptive(image_path, svg_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Failed to load image: {image_path}")
        return

    binary = cv2.adaptiveThreshold(
        img,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=11,
        C=2
    )
    
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    height, width = binary.shape
    dwg = svgwrite.Drawing(svg_path, size=(width, height), viewBox=f"0 0 {width} {height}")
    
    for contour in contours:
        epsilon = 0.001 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        points = [(point[0][0], point[0][1]) for point in approx]
        path_data = "M " + " L ".join(f"{x},{y}" for x, y in points) + " Z"
        dwg.add(dwg.path(d=path_data, fill='black'))

        # points = [(pt[0][0], pt[0][1]) for pt in contour]
        

    
    dwg.save()
    print(f"SVG saved to {svg_path}")

# Tkinter file picker
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
print("Selected file:", file_path)

image_to_svg_silhouette_adaptive(file_path, f'{file_path}.svg')

# image_to_svg_silhouette(file_path, f'{file_path}.svg')
