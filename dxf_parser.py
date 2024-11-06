import os
import ezdxf

def add_point(points, point):
    if point not in points:
        points.append(point)
    return points.index(point)

def print_entity(e):
    start = e.dxf.start
    end = e.dxf.end
    print("Start point:", f"({start.x}, {start.y})", "End point:", f"({end.x}, {end.y})")

def parse_view(folder_path):
    # Initialize dictionaries for each view
    front = {"Points": [], "Lines": []}  # X Z plane looking along +Y axis
    back = {"Points": [], "Lines": []}  # X Z plane looking along -Y axis
    left = {"Points": [], "Lines": []}  # Y Z plane looking along +X axis
    right = {"Points": [], "Lines": []}  # Y Z plane looking along -X axis
    bottom = {"Points": [], "Lines": []}    # X Y plane looking along +Z axis
    top = {"Points": [], "Lines": []}    # X Y plane looking along -Z axis

    for file in os.listdir(folder_path):
        if file.endswith(".dxf"):
            doc = ezdxf.readfile(os.path.join(folder_path, file))
            if file == "Front.dxf":
                parse_entities(doc, front, "XZ")
            if file == "Back.dxf":
                parse_entities(doc, back, "XZ")
            elif file == "Left.dxf":
                parse_entities(doc, left, "YZ")
            elif file == "Right.dxf":
                parse_entities(doc, right, "YZ")
            elif file == "Bottom.dxf":
                parse_entities(doc, bottom, "XY")
            elif file == "Top.dxf":
                parse_entities(doc, top, "XY")
            else:
                print("Invalid file:", file)

    # Simplify edges for each view
    simplify_lines(front)
    simplify_lines(back)
    simplify_lines(left)
    simplify_lines(right)
    simplify_lines(bottom)
    simplify_lines(top)
    
    return front, back, left, right, bottom, top

def project_point(point, projection_plane):
    if projection_plane == "XY": # Top view
        return (int(abs(point.x)), int(abs(point.y)))
    elif projection_plane == "XZ": # Front view
        return (int(abs(point.x)), int(abs(point.y)))
    elif projection_plane == "YZ": # Right view
        return (int(abs(point.x)), int(abs(point.y)))
    else:
        raise ValueError("Invalid projection plane")

def parse_entities(doc, view_dict, projection_plane):
    points = view_dict["Points"]
    lines = view_dict["Lines"]

    for e in doc.modelspace().query('LINE'):
        # Extract and project points onto the specified plane
        start = project_point(e.dxf.start, projection_plane)
        end = project_point(e.dxf.end, projection_plane)

        # Add points and get their indices
        start_idx = add_point(points, start)
        end_idx = add_point(points, end)

        # Store the line as a tuple of indices
        lines.append((start_idx, end_idx))

    for e in doc.modelspace().query('LWPOLYLINE'):
        # Iterate through POLYLINE vertices and create lines between consecutive points
        polyline_points = list(e.vertices_in_wcs())
        first_idx = None
        # Add points and store lines
        for i in range(len(polyline_points) - 1):
            start = project_point(polyline_points[i], projection_plane)
            end = project_point(polyline_points[i + 1], projection_plane)
            start_idx = add_point(points, start)
            end_idx = add_point(points, end)
            lines.append((start_idx, end_idx))
            if i == 0: # Store the index of the first point in the polyline
                first_idx = start_idx
        if e.is_closed:
            end = project_point(polyline_points[-1], projection_plane)
            end_idx = add_point(points, end)
            lines.append((end_idx, first_idx))


def point_on_line(p, a, b):
    """Check if point p lies on the line segment defined by points a and b."""
    cross_product = (b[1] - a[1]) * (p[0] - a[0]) - (b[0] - a[0]) * (p[1] - a[1])
    if int(abs(cross_product) )> 1e-6:
        return False  # Not collinear
    dot_product = (p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])
    if dot_product < 0:
        return False  # p is behind a
    squared_length_ab = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
    if dot_product > squared_length_ab:
        return False  # p is beyond b
    return True  # p is on the line segment


def simplify_lines(view_dict):
    """Simplify lines so no two edges overlap in the view."""
    points = view_dict["Points"]
    lines = view_dict["Lines"]
    new_lines = []

    for start_idx, end_idx in lines:
        a = points[start_idx]
        b = points[end_idx]
        split_points = [start_idx, end_idx]  # Start with endpoints

        # Check if any other point lies on the line segment
        for i, p in enumerate(points):
            if i != start_idx and i != end_idx and point_on_line(p, a, b):
                split_points.append(i)

        # Sort points along the line segment based on their distance to `a`
        split_points = sorted(split_points, key=lambda i: ((points[i][0] - a[0]) ** 2 + (points[i][1] - a[1]) ** 2))

        # Create new line segments between consecutive split points
        for i in range(len(split_points) - 1):
            new_lines.append((split_points[i], split_points[i + 1]))

    # Remove copies of lines and sort the points in each line
    unique_lines = set()
    for line in new_lines:
        unique_lines.add(tuple(sorted(line)))
    
    # Update the list of lines
    view_dict["Lines"] = list(unique_lines)


def neighbour_map(view_dict):
    # convert to point : [(point1, point2), ...] where points are 2D coordinates
    result = {}
    for start_idx, end_idx in view_dict["Lines"]:
        start = view_dict["Points"][start_idx]
        end = view_dict["Points"][end_idx]
        if start not in result:
            result[start] = []
        result[start].append(end)
        if end not in result:
            result[end] = []
        result[end].append(start)
    return result

if __name__ == "__main__":
    folder_path = "./sketches/U"
    front, right, top, _, _, _ = parse_view(folder_path)
    print("Front view:", front, end="\n\n")
    print("Right view:", right, end="\n\n")
    print("Top view:", top, end="\n\n")

    front_neighbours = neighbour_map(front)
    right_neighbours = neighbour_map(right)
    top_neighbours = neighbour_map(top)
    for point, neighbours in front_neighbours.items():
        print(f"Front view: Point {point} has neighbours {neighbours}")
    for point, neighbours in right_neighbours.items():
        print(f"Right view: Point {point} has neighbours {neighbours}")
    for point, neighbours in top_neighbours.items():
        print(f"Top view: Point {point} has neighbours {neighbours}")