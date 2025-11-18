import cv2
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

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


root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
print("Selected file:", file_path)


plot_img(file_path)

