import numpy as np
import svgpathtools
from shapely.geometry import Polygon, LinearRing
import trimesh




def svg_path_to_polygon(svg_path, samples=100):
    points = []
    for i in np.linspace(0, 1, samples):
        point = svg_path.point(i)
        points.append((point.real, point.imag))
    # Close the polygon if not closed
    if points[0] != points[-1]:
        points.append(points[0])
    return points


def polygon_to_3d_mesh(polygon_points, height=1.0):
    """Extrude the 2D polygon points into 3D mesh using trimesh."""
    # Check if polygon_points is valid
    if len(polygon_points) < 3:
        raise ValueError("Not enough points to form a polygon")

    polygon = Polygon(polygon_points)
    
    # Fix invalid polygon
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    
    # After fixing, if still invalid or empty:
    if polygon.is_empty or polygon.area == 0:
        raise ValueError("Polygon is empty or has zero area after fixing")
    
    exterior_coords = np.array(polygon.exterior.coords)
    
    if len(exterior_coords) < 3:
        raise ValueError("Polygon exterior has less than 3 points")
    
    # Create line entities for each edge of the polygon
    entities = []
    for i in range(len(exterior_coords) - 1):
        entities.append(trimesh.path.entities.Line([i, i + 1]))
    
    path = trimesh.path.Path2D(entities=entities, vertices=exterior_coords)
    
    if path.vertices.shape[0] == 0:
        raise ValueError("Path has no vertices")
    
    mesh = path.extrude(height)
    return mesh



def main(svg_file, extrusion_height=1.0):
    # Load SVG paths
    paths, attributes = svgpathtools.svg2paths(svg_file)
    print(f"Is SVG path closed? Start: {paths[0].start}, End: {paths[0].end}")


    # For simplicity, use the first path only
    path = paths[0]

    # Convert path to polygon points
    polygon_points = svg_path_to_polygon(path)

    print(f"Polygon points count: {len(polygon_points)}")
    print(f"Sample points: {polygon_points[:5]}")  # print first 5 points

    # Create 3D mesh from polygon
    mesh = polygon_to_3d_mesh(polygon_points, extrusion_height)

    # Export mesh to STL
    mesh.export('output.stl')
    print("3D model saved as output.stl")

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()

    # Open the file dialog
    file_path = filedialog.askopenfilename()
    print("Selected file:", file_path)
    svg_file = file_path  # Replace with your SVG file path
    print(svg_file)
    main(svg_file)

