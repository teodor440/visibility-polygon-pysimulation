import numpy as np
from scipy.interpolate import interp1d
from collections import namedtuple
from functools import cmp_to_key
import copy

# Some functions will depend that their input should contain this format
Point = namedtuple("Point", "x y")
PolarPoint = namedtuple("PolarPoint", "z r")
Vector = namedtuple("Vector", "x y")
Segment = namedtuple("Segment", "point1 point2")

# List returned as (z, 0) rho phi
def to_polar(points, reference = Point(0, 0)):
    list = []
    for point in points:
        deferenced = Point(point.x - reference.x, point.y - reference.y)
        list.append(PolarPoint(np.sqrt(deferenced.x**2 + deferenced.y**2), np.arctan2(deferenced.y, deferenced.x)))
    return list

# List returned as (z, 0)
def to_cartesian(points, reference = Point(0, 0)):
    list = []
    for point in points:
        list.append(Point(point.x * np.cos(point.y), point.x * np.sin(point.y)))
    return list

def polygon_points(polygon):
    list = []
    for line in polygon.sprites():
        list.append(Point(line.start_position[0], line.start_position[1]))
    return list

def polygon_lines(polygon):
    list = []
    for line in polygon.sprites():
        list.append(Segment(Point(line.start_position[0], line.start_position[1]), Point(line.end_position[0], line.end_position[1])))
    return list

def polygon_intersections(segments):
    points = []
    for first_segment in segments:
        for second_segment in segments:
            if first_segment != second_segment and first_segment.point1 != second_segment.point2 and first_segment.point2 != second_segment.point1:
                intersection = segment_intersection(first_segment, second_segment)
                if intersection:
                    points.append(intersection)

    points_list = [Point(point[0], point[1]) for point in points]
    return points_list

def distance(pointA, pointB):
    return np.sqrt((pointA.x - pointB.x) ** 2 + (pointA.y - pointB.y) ** 2)

def segment_midpoint(segment):
    mid_x = (segment.point1.x + segment.point2.x) / 2
    mid_y = (segment.point1.y + segment.point2.y) / 2
    return Point(mid_x, mid_y)

# Returns negative value when point is to the left of the line, equal on the line, positive to the right
def point_position(point, line):
    first_vector = Point(line.point2.x - line.point1.x, line.point2.y - line.point1.y)  # Vector -> second point - first point
    second_vector = Point(line.point2.x - point.x, line.point2.y - point.y) # Vector -> second point - point
    cross_product = first_vector.x * second_vector.y - first_vector.y * second_vector.x  # Cross product
    return cross_product

def point_identity(point1, point2):
    epsilon = 0.001
    if distance(point1, point2) < epsilon:
        return True
    return False

# If expanding won't work you might like to change the epsilon here
def point_on_open_segment(point, segment):
    epsilon = 0.1
    if distance(point, segment.point1) + distance(point, segment.point2) - distance(segment.point1, segment.point2) >= epsilon:
        return False
    if point_identity(point, segment.point1) or point_identity(point, segment.point2):
        return False
    return True

def sort_points(points, reference):
    sortable_points = [(point, to_polar([point], reference)[0]) for point in points]
    sorted_points = [point[0] for point in sorted(sortable_points, key=lambda sortable: sortable[1].r)]
    return sorted_points

def sort_points_on_polygon(points, polygon_points):
    sorted = []
    vertex1 = polygon_points[0]
    length = len(polygon_points)
    for index in range(1, length + 1):
        vertex2 = polygon_points[index % length]
        to_add_vertices = []
        for point in points:
            if point_identity(vertex1, point):
                 to_add_vertices.append(point)
            elif point_on_open_segment(point, Segment(vertex1, vertex2)):
                 to_add_vertices.append(point)

        sortable_vertices = [(point, distance(point, vertex1)) for point in to_add_vertices]
        sortable_vertices.sort(key=lambda sortable: sortable[1])
        to_add_vertices = [point[0] for point in sortable_vertices]
        for point in to_add_vertices: sorted.append(point)

        vertex1 = vertex2

    return sorted

# Gives p q r colinear checks if q is on [pr]
def on_colinear_segment(p, q, r):
    if q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and \
        q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y):
       return True
    return False

# Returns the orientation of the triple (p, q, r)
# 0 --> p, q and r are colinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def orientation(p, q, r):
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    if val == 0:
        return 0    # colinear

    if val > 0:
        return 1    #clockwise
    else:
        return 2    # counterclock wise

# Check if two segments interset
def check_segment_intersection(first_line, second_line):
    p1, q1 = first_line
    p2, q2 = second_line
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
    if o1 != o2 and o3 != o4:
        return True;
    # Special Cases
    # p1, q1 and p2 are colinear and p2 lies on segment p1q1
    if o1 == 0 and on_colinear_segment(p1, p2, q1): return True;
    # p1, q1 and q2 are colinear and q2 lies on segment p1q1
    if o2 == 0 and on_colinear_segment(p1, q2, q1): return True;
    # p2, q2 and p1 are colinear and p1 lies on segment p2q2
    if o3 == 0 and on_colinear_segment(p2, p1, q2): return True;
    # p2, q2 and q1 are colinear and q1 lies on segment p2q2
    if o4 == 0 and on_colinear_segment(p2, q1, q2): return True;
    return False # Doesn't fall in any of the above cases

# Returns a, b from ax + b = y
def line_equation(line):
    # Compute by solving a linear equation
    variables = np.array([[line.point1.x, 1], [line.point2.x, 1]])
    result = np.array([line.point1.y, line.point2.y])
    x = np.linalg.solve(variables, result)
    return x

# Returns the point of intersection of two segments
def segment_intersection(first_line, second_line):
    if check_segment_intersection(first_line, second_line):
        a1, b1 = line_equation(first_line)
        a2, b2 = line_equation(second_line)
        variables = np.array([[a1, -1], [a2, -1]])
        result = np.array([-b1, -b2])
        x, y = np.linalg.solve(variables, result)
        return Point(x, y)
    return None

def segment_intersections(line, segments):
    list = []
    for segment in segments:
        intersection = segment_intersection(line, segment)
        if intersection:
            list.append(intersection)
    return list

def expand_segment(line, expansion_length):
    line_length = distance(line.point1, line.point2)
    desired_length = line_length + expansion_length
    a, _ = line_equation(line)
    slope = np.arctan(a)

    x_addition_mult = 1
    if line.point2.x < line.point1.x:
        x_addition_mult = -1
    if slope > 0:
        y_addition_mult = 1
        if line.point2.y < line.point1.y:
            y_addition_mult = -1
    else:
        y_addition_mult = -1
        if line.point2.y < line.point1.y:
            y_addition_mult = 1

    x = line.point1.x + x_addition_mult * desired_length * np.cos(slope);
    y = line.point1.y + y_addition_mult * desired_length * np.sin(slope);

    return Segment(Point(line.point1.x, line.point1.y), Point(x, y))

# Will cast a ray with the length of 1000 in both sides to compute the winding number
# If the size of the screen would be greater than this ray_length should be set
def inside_polygon(point, lines, ray_length = 1000):
    winding_number = 0
    ray = Segment(point, Point(point.x + ray_length, point.y))
    for line in lines:
        if check_segment_intersection(ray, line):
            line_direction = line.point2.y - line.point1.y
            if line_direction > 0:
                winding_number = winding_number + 1
            elif line_direction < 0:
                winding_number = winding_number - 1

    if winding_number != 0:
        return True
    else:
        return False

def visible_vertices(point, vertices, edges):
    list = []
    for vertex in vertices:
        segment = Segment(point, vertex)
        intersections = segment_intersections(segment, edges)
        intersections = filter_from_corners(intersections, vertices)
        if len(intersections) == 0:
            list.append(vertex)
    return list


def filter_from_corners(points, filters):
    list = []
    epsilon = 0.001
    for point in points:
        filtered = False
        for filter in filters:
            if distance(point, filter) < epsilon:
                filtered = True
        if not filtered:
            list.append(point)
    return list

# The first point should be the common point
def segment_angle(first_segment, second_segment):
    epsilon = 0.001
    if distance(first_segment.point1, second_segment.point1) > epsilon: raise ValueError("The two segments have different origins: " + str(first_segment) + str(second_segment))
    first_vector = Vector(first_segment.point2.x - first_segment.point1.x, first_segment.point2.y - first_segment.point1.y)
    second_vector = Vector(second_segment.point2.x - second_segment.point1.x, second_segment.point2.y - second_segment.point1.y)
    dot_product = first_vector.x * second_vector.x + first_vector.y * second_vector.y
    first_magnitude = np.sqrt(first_vector.x ** 2 + first_vector.y ** 2)
    second_magnitude = np.sqrt(second_vector.x ** 2 + second_vector.y ** 2)
    cos_tetha = dot_product / (first_magnitude * second_magnitude)
    tetha = np.arccos(cos_tetha)
    return tetha


def expand_visible_vertices(center, vertices, polygon_segments, corners, ray_length = 1000):
    list = []
    vertices_length = len(vertices)
    for index in range(vertices_length):
        vertex = vertices[index]
        list.append(vertex)

        # Get incidence angles
        current_segment = Segment(vertex, center)
        # If program is consistent should always find those two segments
        for segment in polygon_segments:
            if point_identity(segment.point1, vertex): previous_segment = segment
            if point_identity(segment.point2, vertex): next_segment = Segment(segment.point2, segment.point1)
        edges_angle = segment_angle(previous_segment, next_segment)
        first_angle = segment_angle(current_segment, previous_segment)
        second_angle = segment_angle(current_segment, next_segment)
        if edges_angle > np.pi: edges_angle = 2 * np.pi - edges_angle
        if first_angle > np.pi: first_angle = 2 * np.pi - first_angle
        if second_angle > np.pi: second_angle = 2 * np.pi - second_angle

        epsilon = 0.05
        if abs(first_angle + second_angle - edges_angle) < epsilon or \
            abs(first_angle + second_angle + edges_angle - 2 * np.pi) < epsilon:
            continue

        segment = Segment(center, vertex)
        expanded_segment = expand_segment(segment, ray_length)
        intersections = segment_intersections(expanded_segment, polygon_segments)
        intersections = filter_from_corners(intersections, corners)
        comparable_points = [(point, distance(point, center)) for point in intersections]
        intersections = sorted(comparable_points, key=lambda point: point[1])
        if len(intersections) > 0:
            closest = intersections[0][0]
        else:
            closest = None

        if closest != None:
            list.append(closest)
    return list

def is_visible(center, point, segments, corners):
    intersections = segment_intersections(Segment(center, point), segments)
    intersections = filter_from_corners(intersections, corners + [point])
    intersections = [intersection for intersection in intersections if distance(intersection, point) > 0.1]
    if len(intersections) == 0:
        return True
    else:
        return False
