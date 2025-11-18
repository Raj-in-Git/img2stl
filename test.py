
import cv2
import matplotlib.pyplot as plt

def adaptive_threshold_example(image_path, block_size, C):
    # Load grayscale image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found or unable to load.")

    # Make sure block_size is odd and >= 3
    if block_size % 2 == 0:
        block_size += 1
    if block_size < 3:
        block_size = 3

    # Apply adaptive thresholding (inverse binary)
    binary = cv2.adaptiveThreshold(
        img,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=block_size,
        C=C
    )

    # Plot original and binary images
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(img, cmap='gray')
    axs[0].set_title("Original Grayscale")
    axs[0].axis('off')

    axs[1].imshow(binary, cmap='gray')
    axs[1].set_title(f"Adaptive Threshold\nblock_size={block_size}, C={C}")
    axs[1].axis('off')

    plt.show()

    return binary

# Usage example:
if __name__ == "__main__":
    # image_path = r"C:\Users\war4kor\Desktop\My Files\car.webp"  # Replace with your image path

    image_path = r"C:\my_files\Python\My_Apps\img2svg\foreground_grabcut.png"  # Replace with your image path
    adaptive_threshold_example(image_path, block_size=140, C=0)
