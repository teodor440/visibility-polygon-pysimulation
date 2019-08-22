import pygame
import pygame.locals
import math
import time
# This module is experimental and may change with later api
# At least I hoped this would draw things better :(
import pygame.gfxdraw
# My own defined modules
from sprites import Text, Line, Circle, Triangle
from geometry import Point, polygon_lines, polygon_points, polygon_intersections, inside_polygon, visible_vertices, expand_visible_vertices, is_visible, sort_points_on_polygon, sort_points
# Three possible states - draw polygon, pick point, animate, finished
state = "draw polygon"

# Group for all sprites
all = None
# Polygon related vars
polygon = None
# The point of visibility
point = None
# Current polygon line that is drawn onto the screen
polygon_line = None
coord_textfield = None
title_textfield = None
instructions_textfield = None
# Circle to appear when close to first vertex to close the polygon
circle = None
circle_radius = 7
# Where the canvas should begin
offset_y = 0
# Should return a line after adding it to the polygon, else None
# The line is the last polygon line that is drawn, circle is a reference to a circle which should appear when near the first vertex of the polygon to close it
def draw_polygon(clicked, canceled):
    global polygon, polygon_line, circle, vertex_circle, coord_textfield, all, state, offset_y
    mouse_position = pygame.mouse.get_pos()
    # If the cursor is not in the canvas area or overlaps coordinate textfield
    overlaps_tf = (mouse_position[0] < (coord_textfield.rect.x + coord_textfield.rect.width) and mouse_position[1] < (coord_textfield.rect.y + coord_textfield.rect.height))
    if mouse_position[1] < offset_y or overlaps_tf:
        return

    # Compute the distance to the first vertex of the polygon
    if len(polygon.sprites()) > 1:
         first_line = polygon.sprites()[0]
    else:
        first_line = None
    if first_line and len(polygon.sprites()) >= 2:
        distance_from_vertex = math.sqrt(math.pow((first_line.start_position[0] - mouse_position[0]) , 2) + math.pow((first_line.start_position[1] - mouse_position[1]), 2))
    else:
        distance_from_vertex = math.inf

    if clicked:
        # If we began to draw the polygon
        if polygon_line:
            # If we try to close the polygon
            if distance_from_vertex <= circle_radius:
                polygon_line.set_position(polygon_line.start_position, first_line.start_position)
                polygon.add(polygon_line)
                all.add(polygon_line)
                circle.kill()
                circle = None
                state = "pick point"
            else:
                polygon.add(polygon_line)
                polygon_line = Line(polygon_line.end_position, mouse_position)
                all.add(polygon_line)
        # If we should begin to draw the polygon
        else:
            polygon_line = Line(mouse_position, mouse_position)
            all.add(polygon_line)
    # If we didn't click and moved to another frame
    else:
        if polygon_line:
            polygon_line.set_position(polygon_line.start_position, mouse_position)
            # If cursor in range and the polygon has at least one line
            if distance_from_vertex <= circle_radius:
                if circle == None:
                    circle = Circle(first_line.start_position, circle_radius)
                    all.add(circle)
            else:
                if circle:
                    circle.kill()
                    circle = None

    if canceled:
        if polygon_line: polygon_line.kill()
        for line in polygon.sprites():
            line.kill()
        polygon_line = None

    x, y = mouse_position
    coord_textfield.set_text("x = " + str(x) + " y = " + str(int(y - offset_y)))

# When it is to choose a point
def pick_point(clicked, canceled):
    global polygon, offset_y, circle, state, point, all, coord_textfield
    mouse_position = pygame.mouse.get_pos()
    x, y = mouse_position
    coord_textfield.set_text("x = " + str(x) + " y = " + str(int(y - offset_y)))

    if clicked and y >= offset_y:
        if inside_polygon(Point(x, y), polygon_lines(polygon)):
            state = "animate"
            circle = Circle(mouse_position, 2, width = 2)
            all.add(circle)
            point = mouse_position
        else:
            instructions_textfield.set_text("You pressed outside of polygon")
    if canceled:
        state = "draw polygon"

def stage_one_animation():
    global polygon, circle, animated_lines, all, potential_expansion_segments
    point = Point(circle.center[0], circle.center[1])
    polygon_edges = polygon_lines(polygon)
    polygon_vertices = polygon_points(polygon)

    # Compute the points that intersect within the polygon
    intersection_points =  polygon_intersections(polygon_edges)
    # Get the vertices that can be viewed from the point
    vertices = visible_vertices(point, polygon_vertices, polygon_edges)
    # Try to cast a ray from point to vertex and then check if this can expand visibility
    vertices = expand_visible_vertices(point, vertices, polygon_edges, polygon_vertices)

    # Filter the intersection points to the ones visible
    intersection_points = [intersection for intersection in intersection_points if is_visible(point, intersection, polygon_edges, polygon_vertices)]
    # Add the visible intersection points within the polygon to the vertices of the visibility polygon
    vertices = vertices + intersection_points

    # Convert those points to drawable ones
    vertices = [Point(int(round(point.x)), int(round(point.y))) for point in vertices]
    # Sort the vertices of visibility polygon by traversing the original polygon and eliminate duplicates of points
    vertices = list(set(vertices))
    vertices = sort_points_on_polygon(vertices, polygon_vertices)

    # For debugging
    # size = 5
    # for vertex in vertices:
    #     all.add(Circle(vertex, size))
    #     size = size + 3
    #     all.update()
    #     dirty = all.draw(pygame.display.get_surface())
    #     pygame.display.update(dirty)
    #     time.sleep(1)

    last_vertex = None
    first_vertex = None
    for vertex in vertices:
        line = Line(point, vertex)
        animated_lines.add(line)
        all.add(line)

        if last_vertex:
            triangle = Triangle(point, last_vertex, vertex)
            animated_triangles.add(triangle)
            all.add(triangle)
        else:
            first_vertex = vertex
        last_vertex = vertex
    # Draw the last triangle
    triangle = Triangle(point, last_vertex, first_vertex)
    animated_triangles.add(triangle)
    all.add(triangle)

# I wanted to be able to create multiple animation stages
def stage_two_animation():
    pass

# Those are the vertices that can be reached from the polygon
potential_expansion_segments = None
# Animation related vars
animated_lines = pygame.sprite.Group()
animated_triangles = pygame.sprite.Group()
animation_stage = 0
last_animation = None
# This stage animates gradually the polygon and the visible area
def animate_polygon(skip):
    global last_animation, animation_stage, state
    stage_delay = 1
    if not last_animation:
        last_animation = time.time()

    if time.time() - last_animation >= stage_delay:
        last_animation = time.time()
        animation_stage = animation_stage + 1
        if animation_stage == 1:
            stage_one_animation()
        elif animation_stage == 2:
            stage_two_animation()
            state = "finished"

    if skip:
        if animation_stage <= 1: stage_one_animation()
        if animation_stage <= 2: stage_two_animation()
        state = "finished"

def on_state_changed():
    global title_textfield, instructions_textfield, coord_textfield, state, polygon, polygon_line, circle
    if state == "draw polygon":
        title_text = "Draw the polygon"
        instruction_text = "Click to begin drawing the polygon, press escape/backspace to cancel"
        coord_text = "x = 0 y = 0"
        # Clear the old graphics
        for sprite in polygon:
            sprite.kill()
        polygon.empty()
        polygon_line = None
        circle.kill()
        circle = None
        for triangle in animated_triangles:
            triangle.kill()
        animated_triangles.empty()
        for line in animated_lines:
            line.kill()
        animated_lines.empty()
    elif state == "pick point":
        title_text = "Pick a point"
        instruction_text = "Click inside polygon to set point, press escape or backspace to cancel the current polygon"
        coord_text = None
    elif state == "animate":
        title_text = "Computing visible area"
        instruction_text = "Press space to skip"
        coord_text = " "
    elif state == "finished":
        # Clear old animation data
        global last_animation, animation_stage
        last_animation = None
        animation_stage = 0
        title_text = "This is the visible area"
        instruction_text = "Press R to draw again"
        coord_text = " "

    if title_text: title_textfield.set_text(title_text)
    if instruction_text: instructions_textfield.set_text(instruction_text)
    if coord_text: coord_textfield.set_text(coord_text)

def init_window():
    # Presettings for the window
    screen_width = 600
    screen_height = 400
    background_color = pygame.color.Color('white')

    # Draws the window and its background
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Point visibility demo')
    background = pygame.Surface((screen_width, screen_height))
    background.fill(background_color)
    screen.blit(background, (0, 0))

    return screen, background;


def main():
    global polygon, polygon_line, coord_textfield, title_textfield, instructions_textfield, all, state, offset_y
    screen, background = init_window()
    offset_y = 0.2*screen.get_height()
    separation_line_width = 4
    last_state = state

    # The text rendered on the screen
    coord_textfield = Text("x = 0  y = 0", font_size = 14)
    coord_textfield.set_position(5, offset_y)
    title_textfield = Text("Draw the polygon", font_size = 30)
    title_textfield.set_anchor((screen.get_width()/2, 0.25*offset_y))
    instructions_textfield = Text("Click to begin drawing the polygon, press escape/backspace to cancel", font_size = 20)
    instructions_textfield.set_anchor((screen.get_width()/2, 0.6*offset_y))

    # The newly added line to the polygon and the group with the other lines
    separating_line = Line((0, offset_y - separation_line_width), (screen.get_width(), offset_y - separation_line_width), pygame.color.Color('black'), separation_line_width)
    # separating_line = Line((15, 15), (15, 155), (0, 0, 0))
    polygon_line = None
    polygon = pygame.sprite.OrderedUpdates();

    # A group with all sprites for a more efficient rendering
    all = pygame.sprite.RenderUpdates(separating_line, title_textfield, instructions_textfield, coord_textfield)

    all.update()
    all.draw(screen)

    pygame.display.update()

    done = False
    clock = pygame.time.Clock()
    # Loop to run the game into
    while not done:
        # Fps lock
        clock.tick(60)
        # Flags to catch the input
        clicked = False
        canceled = False
        skip = False
        restart = False

        # Now check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    canceled = True
                elif event.key == pygame.K_SPACE:
                    skip = True
                elif event.key == pygame.K_r and state == "finished":
                    restart = True

        # Act accordingly to the current step
        if state == "draw polygon":
            draw_polygon(clicked, canceled)
        elif state == "pick point":
            pick_point(clicked, canceled)
        elif state == "animate":
            animate_polygon(skip)
        elif state == "finished":
            if restart:
                state = "draw polygon"

        if(state != last_state):
            on_state_changed()
            last_state = state

        # Clear the screen where necessary
        all.clear(screen, background)
        # Update the sprites
        all.update()
        # Draw onto the screen
        dirty = all.draw(screen)
        pygame.display.update(dirty)


    pygame.quit()

if __name__ == "__main__":
    main()
