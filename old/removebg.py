import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Globals for mouse callback
drawing = False  # True if mouse is pressed
ix, iy = -1, -1  # Initial x,y
rect = (0, 0, 1, 1)  # Rectangle (x,y,w,h)
img = None
img_copy = None

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, img_copy, rect

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        img_copy = img.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Image - Draw ROI', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('Image - Draw ROI', img_copy)
        x0, y0 = min(ix, x), min(iy, y)
        w, h = abs(x - ix), abs(y - iy)
        rect = (x0, y0, w, h)
        print(f"Selected rectangle: {rect}")

def grabcut_with_rect(image, rect):
    mask = np.zeros(image.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    # Pixels marked as probable/definite foreground
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    foreground = image * mask2[:, :, np.newaxis]
    return foreground

def main():
    global img, img_copy, rect

    # Tkinter dialog to select image
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if not file_path:
        print("No file selected, exiting.")
        return

    img = cv2.imread(file_path)
    if img is None:
        print("Failed to load image.")
        return

    img_copy = img.copy()
    cv2.namedWindow('Image - Draw ROI')
    cv2.setMouseCallback('Image - Draw ROI', draw_rectangle)

    print("Draw a rectangle around the object with your mouse and press 'g' to run GrabCut.")
    print("Press 'q' to quit.")

    while True:
        cv2.imshow('Image - Draw ROI', img_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('g'):
            if rect[2] > 0 and rect[3] > 0:
                foreground = grabcut_with_rect(img, rect)
                cv2.imshow('Extracted Foreground', foreground)
                cv2.imwrite('foreground_grabcut.png', foreground)
                print("Foreground extracted and saved as 'foreground_grabcut.png'")
            else:
                print("Please draw a valid rectangle before running GrabCut.")

        elif key == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
