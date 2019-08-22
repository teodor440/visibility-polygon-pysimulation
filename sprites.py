import pygame

class Ngon(pygame.sprite.Sprite):
    def __init__(self, points, color=pygame.color.Color('black'), animated = True):
        pygame.sprite.Sprite.__init__(self)
        self.points = points
        self.color = color
        self.animated = animated
        if self.animated:
            self.alpha = 0
            self.increase_alpha = True
            self.color = pygame.color.Color(color.r, color.g, color.b, color.a)
        # Python shines :)
        self.min_x = min(point[0] for point in points)
        self.min_y = min(point[1] for point in points)
        self.max_x = max(point[0] for point in points)
        self.max_y = max(point[1] for point in points)
        self.points_on_ngon = [(point[0] - self.min_x, point[1] - self.min_y) for point in points]
        self.rect = pygame.rect.Rect(self.min_x, self.min_y, self.max_x - self.min_x, self.max_y - self.min_y)
        # One extra pixel space for proper display
        self.image = pygame.surface.Surface((self.max_x - self.min_x + 1, self.max_y - self.min_y + 1), pygame.locals.SRCALPHA)
        self.image.set_alpha(0)
        pygame.gfxdraw.filled_polygon(self.image, self.points_on_ngon, self.color)

    def set_color(self, color):
        self.color = color
        if self.animated:
            color.a = self.alpha

    def update(self):
        if self.animated:
            if self.increase_alpha:
                self.alpha = self.alpha + 4
            else:
                self.alpha = self.alpha - 4

            if self.alpha >= 255:
                self.increase_alpha = False
                self.alpha = 255
            elif self.alpha <= 50:
                self.increase_alpha = True
                self.alpha = 50

            self.color.a = self.alpha
            pygame.gfxdraw.filled_polygon(self.image, self.points_on_ngon, self.color)

class Triangle(pygame.sprite.Sprite):
    def __init__(self, first_point, second_point, third_point, color=pygame.color.Color('black'), animated = True):
        pygame.sprite.Sprite.__init__(self)
        self.first_point = first_point
        self.second_point = second_point
        self.third_point = third_point
        self.color = color
        self.animated = animated
        if self.animated:
            self.alpha = 100
            self.increase_alpha = True
            self.color = pygame.color.Color(color.r, color.g, color.b, color.a)
        self.min_x = min(first_point[0], second_point[0], third_point[0])
        self.min_y = min(first_point[1], second_point[1], third_point[1])
        self.max_x = max(first_point[0], second_point[0], third_point[0])
        self.max_y = max(first_point[1], second_point[1], third_point[1])
        self.rect = pygame.rect.Rect(self.min_x, self.min_y, self.max_x - self.min_x, self.max_y - self.min_y)
        self.image = pygame.surface.Surface((self.max_x - self.min_x, self.max_y - self.min_y), pygame.locals.SRCALPHA)
        self.image.set_alpha(0)
        pygame.gfxdraw.filled_trigon(self.image, self.first_point[0] - self.min_x, self.first_point[1] - self.min_y,
            self.second_point[0] - self.min_x, self.second_point[1] - self.min_y, self.third_point[0] - self.min_x, self.third_point[1] - self.min_y, self.color)

    def set_color(self, color):
        self.color = color
        if self.animated:
            color.a = self.alpha

    def update(self):
        if self.animated:
            if self.increase_alpha:
                self.alpha = self.alpha + 10
            else:
                self.alpha = self.alpha - 10

            if self.alpha >= 255:
                self.increase_alpha = False
                self.alpha = 255
            elif self.alpha <= 50:
                self.increase_alpha = True
                self.alpha = 50

            self.color.a = self.alpha
            pygame.gfxdraw.filled_trigon(self.image, self.first_point[0] - self.min_x, self.first_point[1] - self.min_y,
                self.second_point[0] - self.min_x, self.second_point[1] - self.min_y, self.third_point[0] - self.min_x, self.third_point[1] - self.min_y, self.color)


class Circle(pygame.sprite.Sprite):
    def __init__(self, center, radius, color = pygame.color.Color('black'), width = 1, animated = True):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        self.radius = radius
        self.color = color
        self.width = width
        self.animated = animated
        if self.animated:
            self.alpha = 100
            self.increase_alpha = True
            self.color = pygame.color.Color(color.r, color.g, color.b, color.a)
        # For gfxdraw there is a little suplimentary space needed (+2)
        self.image = pygame.surface.Surface((2*radius, 2*radius), pygame.locals.SRCALPHA)
        self.image.set_alpha(0)

        self.rect = pygame.draw.circle(self.image, self.color, (radius, radius), radius, width)
        self.rect.center = center
        # pygame.gfxdraw.circle(self.image, radius, radius, radius, self.color)
        # self.rect = pygame.rect.Rect(center[0]-radius, center[1]-radius, radius, radius)

    def update(self):
        if self.animated:
            if self.increase_alpha:
                self.alpha = self.alpha + 10
            else:
                self.alpha = self.alpha - 10

            if self.alpha >= 255:
                self.increase_alpha = False
                self.alpha = 255
            elif self.alpha <= 80:
                self.increase_alpha = True
                self.alpha = 80

            self.color.a = self.alpha
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, self.width)
            # pygame.gfxdraw.circle(self.image, self.radius, self.radius, self.radius, self.color)

# To draw a sprite in the current way game work you need to have an image=surface and a rect=rectangle associated with it
class Line(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, start_pos, end_pos, color = pygame.color.Color("black"), width=None):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.color = color
        self.set_position(start_pos, end_pos)

    def set_position(self, start_pos, end_pos):
        # There is a bug when trying to draw a antialiased line with the coords 0 on a surface so we ajust vars such that always draw at coords >= 1
        self.start_position, self.end_position = start_pos, end_pos
        offset_x = min(start_pos[0], end_pos[0]) - 1
        offset_y = min(start_pos[1], end_pos[1]) - 1
        self.start_position_on_surface = (start_pos[0] - offset_x, start_pos[1] - offset_y)
        self.end_position_on_surface = (end_pos[0] - offset_x, end_pos[1] - offset_y)
        # The thickness of a aaline is 2
        width = abs(start_pos[0] - end_pos[0]) + 3
        height = abs(start_pos[1] - end_pos[1]) + 3

        self.image = pygame.surface.Surface((width, height))
        # Make surface transparent
        # This is achieved by considering the colorkey=white pixels as transparent
        colorkey = pygame.color.Color('white')
        self.image.set_colorkey(colorkey)
        self.image.fill(colorkey)
        # Finally draw the line and get the rectangle occupied by it
        # If it shouldn't have a certain width draw an antialiased line
        if self.width == None:
            # self.rect = pygame.draw.aaline(self.image, self.color, self.start_position_on_surface, self.end_position_on_surface);
            pygame.gfxdraw.line(self.image, self.start_position_on_surface[0], self.start_position_on_surface[1], self.end_position_on_surface[0], self.end_position_on_surface[1],self.color)
            self.rect = pygame.rect.Rect(offset_x, offset_y, abs(self.start_position[0] - self.end_position[0]), abs(self.start_position[1] - self.end_position[1]))
        else:
            self.rect = pygame.draw.line(self.image, self.color, self.start_position_on_surface, self.end_position_on_surface, self.width)
        self.rect.x = offset_x
        self.rect.y = offset_y

class Text(pygame.sprite.Sprite):
    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, text = "", color = pygame.color.Color('black'), font_size = 24):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        # Set the text and position it
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.anchor = None
        self.x = None
        self.y = None
        self.set_text(text)
        self.rect = self.image.get_rect()


    def set_position(self, left, top):
        self.rect = self.image.get_rect(x = left, y = top)
        self.x = left
        self.y = top
        self.anchor = None

    def set_anchor(self, center_anchor):
        self.anchor = center_anchor
        self.x = self.y = None
        x, y = center_anchor
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def set_text(self, text):
        self.image = self.font.render(text, 1, self.color)
        if self.anchor:
            self.rect = self.image.get_rect()
            x, y = self.anchor
            self.rect.centerx = x
            self.rect.centery = y
        elif self.x and self.y:
            self.image.get_rect(x = self.x, y = self.y)
