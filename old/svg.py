# with adaptive thresholding
import cv2
import numpy as np
import svgwrite
import tkinter as tk
from tkinter import filedialog


def image_to_svg_silhouette_adaptive(image_path, svg_path):
    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply adaptive thresholding to get a clean black/white silhouette
    binary = cv2.adaptiveThreshold(
        img,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=11,  # size of neighborhood to calculate threshold
        C=2            # constant subtracted from mean
    )
    
    # Find contours (external only)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create SVG drawing
    height, width = binary.shape
    dwg = svgwrite.Drawing(svg_path, size=(width, height))
    
    # Add black filled paths for each contour
    for contour in contours:
        points = [(point[0][0], point[0][1]) for point in contour]
        path_data = "M " + " L ".join(f"{x},{y}" for x, y in points) + " Z"
        dwg.add(dwg.path(d=path_data, fill='black'))
    
    dwg.save()
    print(f"SVG saved to {svg_path}")

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
print("Selected file:", file_path)


# # Example usage:
image_to_svg_silhouette_adaptive(file_path, 'output.svg')