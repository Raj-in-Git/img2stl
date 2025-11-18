import cv2
import numpy as np
import svgwrite
import tkinter as tk
from tkinter import filedialog, messagebox

class AdaptiveSVGConverter:
    def __init__(self, master):
        self.master = master
        master.title("Adaptive Threshold to SVG")

        # Variables
        self.block_size = tk.IntVar(value=11)
        self.C = tk.IntVar(value=2)
        self.image_path = None
        self.binary_image = None

        # Widgets
        tk.Button(master, text="Select Image", command=self.select_image).grid(row=0, column=0, columnspan=2, pady=5)

        tk.Label(master, text="Block Size (odd ≥ 3):").grid(row=1, column=0, sticky="e")
        self.block_slider = tk.Scale(master, from_=3, to=51, resolution=2, orient=tk.HORIZONTAL, variable=self.block_size)
        self.block_slider.grid(row=1, column=1, sticky="w")

        tk.Label(master, text="C (integer):").grid(row=2, column=0, sticky="e")
        self.c_slider = tk.Scale(master, from_=-20, to=20, orient=tk.HORIZONTAL, variable=self.C)
        self.c_slider.grid(row=2, column=1, sticky="w")

        tk.Button(master, text="Preview Silhouette", command=self.preview).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(master, text="Save SVG", command=self.save_svg).grid(row=4, column=0, columnspan=2, pady=5)

    def select_image(self):
        path = filedialog.askopenfilename(title="Select image file",
                                          filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.image_path = path
            messagebox.showinfo("Image Selected", f"Selected: {path}")
        else:
            messagebox.showwarning("No file", "No file was selected.")

    def apply_adaptive_threshold(self):
        if not self.image_path:
            messagebox.showwarning("No image", "Please select an image first.")
            return None

        img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            messagebox.showerror("Error", "Failed to load the image.")
            return None

        block = self.block_size.get()
        # blockSize must be odd and >=3; enforce this:
        if block % 2 == 0:
            block += 1
        if block < 3:
            block = 3

        binary = cv2.adaptiveThreshold(
            img,
            maxValue=255,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
            thresholdType=cv2.THRESH_BINARY_INV,
            blockSize=block,
            C=self.C.get()
        )
        self.binary_image = binary
        return binary

    def preview(self):
        binary = self.apply_adaptive_threshold()
        if binary is not None:
            cv2.imshow("Silhouette Preview", binary)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def save_svg(self):
        binary = self.apply_adaptive_threshold()
        if binary is None:
            return

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        height, width = binary.shape
        dwg = svgwrite.Drawing("output.svg", size=(width, height), viewBox=f"0 0 {width} {height}")

        for contour in contours:
            epsilon = 0.01 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            points = [(pt[0][0], pt[0][1]) for pt in approx]
            path_data = "M " + " L ".join(f"{x},{y}" for x, y in points) + " Z"
            dwg.add(dwg.path(d=path_data, fill='black'))

        dwg.save()
        messagebox.showinfo("SVG Saved", "SVG file saved as 'output.svg'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdaptiveSVGConverter(root)
    root.mainloop()
