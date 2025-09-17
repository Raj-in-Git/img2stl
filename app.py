import cv2
import numpy as np
import svgwrite
import tkinter as tk
from tkinter import filedialog, messagebox
import svgpathtools
import trimesh
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import os
import triangle
import scipy
import trimesh


def image_to_svg_silhouette_adaptive(image_path, svg_path, block_size=140, C=0):
    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Failed to load image")

    # Ensure block_size is odd and >=3
    if block_size % 2 == 0:
        block_size += 1
    if block_size < 3:
        block_size = 3

    print(f"Applying adaptive threshold with block_size={block_size}, C={C}...")
    binary = cv2.adaptiveThreshold(
        img,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=block_size,
        C=C
    )

    cv2.imwrite("debug_binary.png", binary)  # Save binary for inspection
    print("Saved binary threshold image as debug_binary.png")

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} contours.")

    height, width = binary.shape
    dwg = svgwrite.Drawing(svg_path, size=(width, height), viewBox=f"0 0 {width} {height}")

    for i, contour in enumerate(contours):
        points = [(pt[0][0], pt[0][1]) for pt in contour]
        if len(points) > 2:
            path_data = "M " + " L ".join(f"{x},{y}" for x, y in points) + " Z"
            dwg.add(dwg.path(d=path_data, fill='black'))
        else:
            print(f"Contour {i} ignored due to insufficient points.")

    dwg.save()
    print(f"SVG saved to: {svg_path}")

    if not os.path.exists(svg_path):
        raise FileNotFoundError("SVG file was not created successfully.")


def path_to_polygon(path, samples=200):
    points = []
    for seg in path:
        for t in np.linspace(0, 1, samples):
            p = seg.point(t)
            points.append((p.real, p.imag))
    polygon = Polygon(points)
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    return polygon


def svg_to_shapely_polygons(svg_file):
    print(f"Parsing SVG file: {svg_file}")
    paths, _ = svgpathtools.svg2paths(svg_file)
    print(f"Number of paths found in SVG: {len(paths)}")

    polygons = []
    for i, path in enumerate(paths):
        poly = path_to_polygon(path, samples=200)
        if poly.is_valid and poly.area > 0:
            polygons.append(poly)
            print(f"Polygon {i} area: {poly.area:.2f}")
        else:
            print(f"Polygon {i} invalid or zero area, ignored.")

    combined = unary_union(polygons)
    print(f"Combined polygon area: {combined.area:.2f}")
    if combined.is_empty:
        raise ValueError("No valid polygons found in SVG.")
    return combined


# def shapely_to_trimesh(polygon, height=10):
#     print("Converting shapely polygon(s) to trimesh 3D mesh...")
#     if isinstance(polygon, Polygon):
#         polygons = [polygon]
#     elif isinstance(polygon, MultiPolygon):
#         polygons = list(polygon.geoms)
#     else:
#         raise ValueError("Unsupported geometry type")

#     entities = []
#     vertices = []
#     vert_offset = 0

#     for poly_idx, poly in enumerate(polygons):
#         exterior = np.array(poly.exterior.coords)
#         vertices.extend(exterior.tolist())
#         n = len(exterior)
#         indices = list(range(vert_offset, vert_offset + n))
#         vert_offset += n
#         for i in range(n - 1):
#             entities.append(trimesh.path.entities.Line([indices[i], indices[i + 1]]))

#         # Close the exterior contour
#         entities.append(trimesh.path.entities.Line([indices[-1], indices[0]]))

#         for interior in poly.interiors:
#             interior_coords = np.array(interior.coords)
#             vertices.extend(interior_coords.tolist())
#             m = len(interior_coords)
#             indices_hole = list(range(vert_offset, vert_offset + m))
#             vert_offset += m
#             for j in range(m - 1):
#                 entities.append(trimesh.path.entities.Line([indices_hole[j], indices_hole[j + 1]]))
#             # Close hole contour
#             entities.append(trimesh.path.entities.Line([indices_hole[-1], indices_hole[0]]))

#     path2d = trimesh.path.Path2D(entities=entities, vertices=np.array(vertices))
#     mesh_3d = path2d.extrude(height)
#     print("Extrusion complete.")
#     return mesh_3d



def shapely_to_trimesh(polygon, height=10):
    if isinstance(polygon, Polygon):
        polygons = [polygon]
    elif isinstance(polygon, MultiPolygon):
        polygons = list(polygon.geoms)
    else:
        raise ValueError("Unsupported geometry type")

    meshes = []

    for poly in polygons:
        exterior = np.array(poly.exterior.coords)
        entities = []
        vertices = []
        vert_offset = 0

        vertices.extend(exterior.tolist())
        n = len(exterior)
        indices = list(range(vert_offset, vert_offset + n))
        vert_offset += n
        for i in range(n - 1):
            entities.append(trimesh.path.entities.Line([indices[i], indices[i + 1]]))

        for interior in poly.interiors:
            interior_coords = np.array(interior.coords)
            vertices.extend(interior_coords.tolist())
            m = len(interior_coords)
            indices_hole = list(range(vert_offset, vert_offset + m))
            vert_offset += m
            for j in range(m - 1):
                entities.append(trimesh.path.entities.Line([indices_hole[j], indices_hole[j + 1]]))

        path2d = trimesh.path.Path2D(entities=entities, vertices=np.array(vertices))
        mesh_3d = path2d.extrude(height)
        meshes.append(mesh_3d)

    # Combine all meshes into one
    combined_mesh = trimesh.util.concatenate(meshes)
    return combined_mesh



def convert_svg_to_3d(svg_file, output_stl, height=10):
    polygon = svg_to_shapely_polygons(svg_file)
    mesh = shapely_to_trimesh(polygon, height)
    mesh.export(output_stl)
    print(f"STL saved to: {output_stl}")


def process_image_to_stl(image_path):
    base_dir = os.path.dirname(os.path.abspath(image_path))
    svg_path = os.path.join(base_dir, "temp_output.svg")
    stl_path = os.path.join(base_dir, "output.stl")

    print("Starting image to SVG silhouette conversion...")
    image_to_svg_silhouette_adaptive(image_path, svg_path)

    print("Starting SVG to 3D STL conversion...")
    convert_svg_to_3d(svg_path, stl_path)

    return stl_path

def processfile():
    file_path = filedialog.askopenfilename(
        title="Select image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
    )
    if not file_path:
        messagebox.showwarning("No file", "No file selected, exiting.")
        return

    try:
        stl_file = process_image_to_stl(file_path)
        messagebox.showinfo("Success", f"STL generated and saved as:\n{stl_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process image:\n{e}")
        print(f"Error: {e}")


# def main():

# if __name__ == "__main__":
#     main()


root = tk.Tk()
root.title("Upload Image File")
upload_button = tk.Button(root, text="Upload Image File", command=processfile)
upload_button.pack(pady=20, padx=20)
root.mainloop()