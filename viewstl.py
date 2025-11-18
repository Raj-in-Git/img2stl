from stl import mesh
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import pyvista as pv
from stl import mesh

def viewStl(stl_path):
    # Load the STL file
    your_mesh = mesh.Mesh.from_file(stl_path)

    # Create a new plot
    figure = plt.figure()
    axes = mplot3d.Axes3D(figure)

    # Load the vectors from the STL mesh and add them to the plot
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

    # Auto scale to the mesh size
    scale = your_mesh.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)

    plt.show()


def viewpystl(stl_path):
    # Read STL file
    your_mesh = mesh.Mesh.from_file(stl_path)

    # Create a PyVista mesh
    points = your_mesh.vectors.reshape(-1, 3)
    faces = []
    for i in range(len(your_mesh.vectors)):
        faces.append([3, i*3, i*3+1, i*3+2])  # '3' means triangle with 3 points

    faces = [item for sublist in faces for item in sublist]  # flatten the list
    pv_mesh = pv.PolyData(points, faces)

    # Plot using pyvista
    plotter = pv.Plotter()
    plotter.add_mesh(pv_mesh, color='lightblue')
    plotter.show()



def upload_file():
    filepath = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
    )
    if filepath:
        print("Selected file:", filepath)
        viewpystl(filepath)
        # You can add code here to process the file



root = tk.Tk()
root.title("Upload STL File")

upload_button = tk.Button(root, text="Upload STL File", command=upload_file)
upload_button.pack(pady=20, padx=20)

root.mainloop()






