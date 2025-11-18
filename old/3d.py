import cv2
import numpy as np
import svgwrite
import tkinter as tk
from tkinter import filedialog, messagebox
import svgpathtools
import trimesh
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union


def image_to_svg_silhouette_adaptive(image_path, svg_path, block_size=11, C=2):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Failed to load image")

    # Ensure block_size is odd and >=3
    if block_size % 2 == 0:
        block_size += 1
    if block_size < 3:
        block_size = 3

    binary = cv2.adaptiveThreshold(
        img,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=block_size,
        C=C
    )

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height, width = binary.shape

    dwg = svgwrite.Drawing(svg_path, size=(width, height), viewBox=f"0 0 {width} {height}")

    for contour in contours:
        points = [(pt[0][0], pt[0][1]) for pt in contour]
        if len(points) > 2:
            path_data = "M " + " L ".join(f"{x},{y}" for x, y in points) + " Z"
            dwg.add(dwg.path(d=path_data, fill='black'))

    dwg.save()


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
    paths, _ = svgpathtools.svg2paths(svg_file)
    polygons = []
    for path in paths:
        poly = path_to_polygon(path, samples=200)
        if poly.is_valid and poly.area > 0:
            polygons.append(poly)
    combined = unary_union(polygons)
    return combined


def shapely_to_trimesh(polygon, height=10):
    if isinstance(polygon, Polygon):
        polygons = [polygon]
    elif isinstance(polygon, MultiPolygon):
        polygons = list(polygon.geoms)
    else:
        raise ValueError("Unsupported geometry type")

    entities = []
    vertices = []
    vert_offset = 0

    for poly in polygons:
        exterior = np.array(poly.exterior.coords)
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
    return mesh_3d


def convert_svg_to_3d(svg_file, output_stl, height=10):
    polygon = svg_to_shapely_polygons(svg_file)
    mesh = shapely_to_trimesh(polygon, height)
    mesh.export(output_stl)


def process_image_to_stl(image_path):
    svg_path = "temp_output.svg"
    stl_path = "output.stl"

    # Convert image to SVG silhouette
    image_to_svg_silhouette_adaptive(image_path, svg_path)

    # Convert SVG silhouette to 3D STL
    convert_svg_to_3d(svg_path, stl_path)

    return stl_path


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title="Select image",
                                           filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    if not file_path:
        messagebox.showwarning("No file", "No file selected, exiting.")
        return

    try:
        stl_file = process_image_to_stl(file_path)
        messagebox.showinfo("Success", f"STL generated and saved as:\n{stl_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process image:\n{e}")


if __name__ == "__main__":
    main()
