import pygame, math, numba, timeit

pygame.init()

win = pygame.display.set_mode((1300, 700)) # set pygame window to 1300x700

win_width = win.get_width()
win_height = win.get_height()

#RENDERLIST is cleared every frame
RENDERLIST = [] # everything to be rendered gets appended to this list, then the redrawgamewindow decides how to blit/draw it to the window.

# sort by fourth element in sub-list, this is where distance is stored when an item is appended to RENDERLIST
# TLDR depth sort
def sort_by_i4(i):
    return i[3]


class Player:
    def __init__(self, x, y, direction=0, fov=90):
        """
        a class representing the player, the camera, and part of the renderer
        :param x: position along the x- in world spaceaxis
        :param y: position along the y-axis
        :param direction: direction in degrees
        """
        self.p = pygame.Vector2(x, y)
        self.d = direction
        self.fov = fov

    def move_forward(self):
        self.p.x += (math.cos(math.radians(self.d)) * 5)
        self.p.y += (math.sin(math.radians(self.d)) * 5)

    def move_backward(self):
        self.p.x -= (math.cos(math.radians(self.d)) * 5)
        self.p.y -= (math.sin(math.radians(self.d)) * 5)

    def move_left(self):
        self.d -= 90
        self.move_forward()
        self.d += 90

    def move_right(self):
        self.d += 90
        self.move_forward()
        self.d -= 90


    #draws the player as if they were in a top-down world, showing their direction and position. Useful for debugging movement code
    def debug_draw(self):
        pygame.draw.rect(win, (0, 0, 255), (self.p.x - 5, self.p.y - 5, 10, 10))
        pygame.draw.line(win, (0, 0, 255), (self.p.x, self.p.y), (self.p.x + (math.cos(math.radians(self.d)) * 30), self.p.y + (math.sin(math.radians(self.d)) * 30)), 1)


    # renderer+camera functions below vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    # takes an angle, in worldspace, and ives a position along the x axis it should appear in.
    def angle_to_screenspace(self, theta):
        """
        :param theta:
        :return: -1 if out of the fov. otherwise a value between 0 and 1
        """
        L = round(self.d - (self.fov / 2))
        R = round(self.d + (self.fov / 2))
        #pygame.draw.line(win, (255, 0, 255), (self.p.x, self.p.y), (self.p.x + (math.cos(math.radians(L)) * 300), self.p.y + (math.sin(math.radians(L)) * 300)), 1)
        #pygame.draw.line(win, (255, 0, 255), (self.p.x, self.p.y), (self.p.x + (math.cos(math.radians(R)) * 300), self.p.y + (math.sin(math.radians(R)) * 300)), 1)
        U = (theta - L) / self.fov
        U_screen = U % 1
        U_whole = U - U_screen
        if U_whole > -4 and U_screen < 0:
            U_screen += U_whole
        return U_screen

    def draw_point(self, point):
        angle = pygame.Vector2(0, 0).angle_to((self.p.x - point.p.x, self.p.y - point.p.y)) + 180
        #pygame.draw.line(win, (0, 0, 255), (self.p.x, self.p.y), (self.p.x + 500, self.p.y), 1)

        normalised_x = self.angle_to_screenspace(angle)
        draw_x = normalised_x * win_width

        distance = self.p.distance_to(point.p)

        # some code for culling, and also fixing an issue where the drawing would sometimes not occur when the angle 0 (worldspace) is visible
        # Define far left and far right sides of the FOV
        L = round(self.d - (self.fov / 2))
        R = round(self.d + (self.fov / 2))
        # ensure that all  angles are not larger than 360 degrees, this was part of the issue, as the object would sometimes be drawn off screen due to the angle being too large
        L %= 360
        R %= 360
        angle %= 360

        if L < R: # this is the actual culling code. If the angle 0 (worldspace) is not visible, L will be smaller than R. 
            if angle < L or angle > R: # angle will be between L and R if visible if on screen, so if not, return nothing
                return
        
        elif angle < L and angle > R:
            return

        # Just some code yoinked from my raycaster to determine the height of a thing on screen depending on its distance. There are way better ways of doing it, I will implement one in the future
        height = (35000 / distance) + 350
        y = round(-350 - height) + 1000
        height -= y
        c = (255, 0, 255)

        pygame.draw.rect(win, c, (draw_x, y, 10, height))

    # Same wthing as draw_point(), but returns the data instead of drawing it.(width is omitted as it is considered constant for a point regardless of distance)
    def drawn_point(self, point):
        angle = pygame.Vector2(0, 0).angle_to((self.p.x - point.p.x, self.p.y - point.p.y)) + 180
        #pygame.draw.line(win, (0, 0, 255), (self.p.x, self.p.y), (self.p.x + 500, self.p.y), 1)

        normalised_x = self.angle_to_screenspace(angle)
        draw_x = normalised_x * win_width

        distance = self.p.distance_to(point.p)

        # "CULL THE WEAK!!!" - John Seed I think
        L = round(self.d - (self.fov / 2))
        R = round(self.d + (self.fov / 2))
        L %= 360
        R %= 360
        angle %= 360

        if L < R:
            if angle < L or angle > R:
                return

        elif angle < L and angle > R:
            return

        height = (35000 / distance) + 350
        y = round(-350 - height) + 1000
        height -= y

        return [draw_x, y, height]


class Point:
    points = [] # a list of all points, is looped over in redrawgamewindow() and the info of each 
    def __init__(self, x, y):
        """
        A base class for anything that needs to be represented by a point in space.
        :param x: position along the x-axis in world space
        :param y: position along the y-axis in world space
        :param col: colour (r, g, b)
        :return:
        """
        self.p = pygame.Vector2(x, y)
        self.col = col = (255, 255, 0)
        self.lpos = len(Point.points) - 1

        Point.points.append(self)

    def begone(self): # youtube friendly version of kill
        try: # required a try:except block as for some reason if there was only one point in existence it would not be in the list? may have been fixed, I'll have to test it out later
            Point.points.pop(self.lpos)
        except Exception:
            Point.points = []

    def debug_draw(self, scale=3): # same top-down view as the player debug draw
        pygame.draw.rect(win, self.col, (self.p.x - (scale * 0.5), self.p.y - (scale * 0.5), scale, scale))

    def get_angle(self, pos):
        pos = pygame.Vector2(pos)
        angle = self.p.angle_to(pos) + 180

        return angle


class Tree: # esentially a point with a sprite that scales vertically and horizontally
    trees = [] # like Point.points, but for trees and appends the direction as well for the depth sort
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.p = pygame.Vector2(x, y) # where it is on the world (remember, this is 2.5D so no z)
        self.img = pygame.image.load(("assets\\Tree1.png")).convert() # .convert() is to make resizing and drawing faster
        self.direction = 0 # For if I try to change the sprite depending on the direction from the sprite to the player, similar to games like DOOM
        #self.rect = pygame.rect.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        Tree.trees.append(self)

    def get_view_dimensions(self, pl):
        angle = pygame.Vector2(0, 0).angle_to((pl.p.x - self.p.x, pl.p.y - self.p.y)) + 180
        #pygame.draw.line(win, (0, 0, 255), (pl.p.x, pl.p.y), (self.p.x + 500, self.p.y), 1)

        normalised_x = pl.angle_to_screenspace(angle) # uses the same function as a Point to get its screenspace position from its angle
        draw_x = normalised_x * win_width

        distance = pl.p.distance_to(self.p)

        # ik it's wierd but this is just how I kept the aspect ratio of the sprite constant
        A = (35000 / (distance + 1)) + 350 # you'd think the 350 can be simplified out, but i guess i'm too stupid to figure it out
        B = round(-350 - A) + 1000
        A -= B
        width = A

        # same culling code as Point, should reformat into a function as it's repeated multiple times
        L = round(pl.d - (pl.fov / 2))
        R = round(pl.d + (pl.fov / 2))
        L %= 360
        R %= 360
        angle %= 360

        if L < R:
            if angle < L or angle > R:
                return

        elif angle < L and angle > R:
            return

        height = (35000 / (distance + 1)) + 350
        y = round(-350 - height) + 1000
        height -= y

        return [draw_x, y, height, width, distance]

    def draw(self):
        dimensions = self.get_view_dimensions(pl)
        try:
            # sprite draw
            i_copy = self.img.copy()
            im = pygame.transform.scale(i_copy, (dimensions[3], dimensions[2]))
            im.set_colorkey((255, 255, 255)) # enables tranparency
            x = dimensions[0]
            y = dimensions[1]
            RENDERLIST.append((im, x - (im.get_width() / 2), y, dimensions[4]))
            # direction line test
            #pygame.draw.rect(win, (255, 0, 0), (x, y + im.get_height(), 10, 10))
            origin = pygame.Vector2(x, y + im.get_height())
            direction_vect_visualisation = pygame.Vector2(math.cos(math.radians(self.direction - pl.d)), math.sin(math.radians(self.direction - pl.d)))
            pygame.draw.line(win, (255, 0, 0), origin, origin + (direction_vect_visualisation * 50), 3) # to help debugging when changing sprite depending on direction
        except Exception as e:
            if e.__str__() != "'NoneType' object is not subscriptable":
                print(e)


class Box: # This is a sprite stack, a bunch of rotated sprites that look like a 3D object on the ground
    boxes = []
    # hit detection can be done in draw(), as z may be distance from player view plane, but it's also culled so must be within sight and close to view plane to have a low z.
    def __init__(self, x, y, directory_to_sprite_stack="assets/prism sprite stack test", amount_of_sprites=7):
        self.x = x
        self.y = y
        self.p = pygame.Vector2(x, y)
        self.direction = 0
        images_temp = []
        for i in range(amount_of_sprites):
            images_temp.append(pygame.image.load(f"{directory_to_sprite_stack}/layer {i + 1}.png").convert())
            print(f"{directory_to_sprite_stack}/layer {i + 1}")
            images_temp[-1] = pygame.transform.scale(images_temp[-1], (images_temp[-1].get_width() * 2, images_temp[-1].get_height() * 2))
        self.images = [i for i in images_temp]

        for i in self.images:
            i.set_colorkey((0, 0, 0))

        self.sprite_stack_jump = 500 # how much higher each stack should be from each other (must be a really big change to be noticeable)

        Box.boxes.append(self)

    def get_view_dimensions(self):
        angle = pygame.Vector2(0, 0).angle_to((pl.p.x - self.p.x, pl.p.y - self.p.y)) + 180
        #pygame.draw.line(win, (0, 0, 255), (pl.p.x, pl.p.y), (self.p.x + 500, self.p.y), 1)

        normalised_x = pl.angle_to_screenspace(angle)
        draw_x = normalised_x * win_width

        distance = pl.p.distance_to(self.p)

        # ik it's wierd but this is just how I kept the aspect ratio of the sprite constant
        A = (35000 / (distance + 1)) + 350
        B = round(-350 - A) + 1000
        A -= B
        width = A

        # same culling code as before, I really need to make this a function
        L = round(pl.d - (pl.fov / 2))
        R = round(pl.d + (pl.fov / 2))
        L %= 360
        R %= 360
        angle %= 360

        if L < R:
            if angle < L or angle > R:
                return

        elif angle < L and angle > R:
            return

        height = (35000 / (distance + 1)) + 350
        y = round(-350 - height) + 1000
        height -= y

        return [draw_x, y, height, width, distance]

    @numba.jit() # not sure how much numba is helping here
    def draw(self):
        dimensions = self.get_view_dimensions()
        if type(dimensions) == type(None):
            return
        # sprite draw
        x = dimensions[0]
        y = dimensions[1]
        z = dimensions[4]
        height = dimensions[2]
        z_normalised = z / 1300
        scale = 0.1
        SH = (height / win_height) * scale
        origin = pygame.Vector2(x, y + dimensions[2]) # center of current sprite stack
        direction_to_rotate_images = self.direction - pl.d
        current_y = origin.y
        sep_dist = (self.sprite_stack_jump // len(self.images)) * SH
        images_todraw = []
        for i in self.images:
            iC = i.copy()

            #iC = pygame.transform.scale(iC, ((1 / scale) * iC.get_width(), ((1 / scale) * iC.get_height())))

            iC = pygame.transform.rotate(iC, - direction_to_rotate_images)

            iC = pygame.transform.scale(iC, (((iC.get_width() * 10) // z_normalised) * scale, ((iC.get_height() * 10) / 2 // z_normalised) * SH))
            iC.set_colorkey((0, 0, 0))

            images_todraw.append((iC, (origin.x - iC.get_width() / 2, current_y - iC.get_height() / 2)))

            current_y -= sep_dist
#        images_todraw = []
#        # loop through images
#        for i in self.images:
#            # place on top of previous, difference in screenspace y is divided by z
#            origin.y -= self.sprite_stack_jump // z_normalised # must be integer divide as it's a screen space position
#
#            # rotate around centre and .convert()
#            i_copy = i.copy()
#            #pygame.transform.rotate(i_copy, direction_to_rotate_images).convert() # change to rotate around center
#
#            # divide height of rotated image by z
#            i_copy = pygame.transform.scale(i_copy, (i_copy.get_width() * 10 // z_normalised, i_copy.get_height() * 10 // z_normalised))
#
#            # append to list that will be added to RENDERLIST
#            pygame.draw.rect(win, (255, 0, 0), (origin.x, origin.y, 10, 10))
#            images_todraw.append((i_copy, origin))
#
#        # to debug, draws a line from origin in the direction
#        #direction_vect_visualisation = pygame.Vector2(math.cos(math.radians(direction_to_rotate_images)), math.sin(math.radians(direction_to_rotate_images)))
#        #pygame.draw.line(win, (255, 0, 0), origin, origin + (direction_vect_visualisation * 50), 3)

        # 3rd element is the one it's sorting by, so it must be z
        RENDERLIST.append((images_todraw, 0, 0, z))


class HUD:
    weapon = pygame.image.load("assets/hud 1.png")
    weapon_y_offset = 0


# misc essential functions -------------------------------------------------------------------------#
pl = Player(win_width / 2, win_height / 2)

#hud = pygame.image.load("assets/hud 1.png")

def redrawgamewindow(p1=0, p2=0):
    #win.fill((255, 255, 255))
    # 2.5D world render
    pygame.draw.rect(win, (0, 255, 0), (0, win_height / 2, win_width, win_height / 2))
    pygame.draw.rect(win, (70, 120, 255), (0, 0, win_width, win_height / 2))
    # loop over each object and put it's data into RENDERLIST
    if len(Point.points) > 0:
        for p in Point.points:
            pl.draw_point(p)
    if len(Tree.trees) > 0:
        for t in Tree.trees:
            t.draw()
    if len(Box.boxes) > 0:
        for b in Box.boxes:
            b.draw()
    # sore RENDERLIST by distance then draw everything to window
    if len(RENDERLIST) > 0:
        RENDERLIST.sort(key=sort_by_i4, reverse=True)
        for i in RENDERLIST:
            if type(i[0]) == pygame.surface.Surface: # if tree then blit tree
                win.blit(i[0], (i[1], i[2]))
            else: # box
                for s in i[0]:
                    win.blit(s[0], s[1])

    # HUD render
    win.blit(HUD.weapon, (0, 0))

    # window update
    pygame.display.update()

    # clear RENDERLIST
    RENDERLIST.clear()

    # debug
    #pl.debug_draw()


# mainloop -----------------------------------------------------------------------------------------#
run = True
pointing = False
clock = pygame.time.Clock()

# for testing performance. Small size of sprites is like an automatic lod for distant objects, even 100 is super fast from far away. but up close it gets very slow.
#for i in range(50):
#    Box(100 + i // 50, 100 + i // 50)
Box(100, 100)

mouse_pos = pygame.mouse.get_pos()
mouse_x = mouse_pos[0]
mouse_y = mouse_pos[1]

del_cooldown = False # cooldown on deleting points added by clicking, there's a cooldown so you can't delete 60 each second
looking = False # if looking, the players mouse movements are interpreted as looking around.
while run:
    clock.tick(60)

    redrawgamewindow()

    if pointing:
        try:
            Point.points.pop(-1)
        except: pass

    mouse_pos = pygame.mouse.get_pos()
    mouse_rel = pygame.mouse.get_rel()
    mouse_x = mouse_pos[0]
    mouse_y = mouse_pos[1]

    if pointing:
        bPoint = Point(mouse_x, mouse_y)
    if looking:
        pl.d += mouse_rel[0] / 5

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pointing = True
            if looking:
                pass # do animation

        if event.type == pygame.MOUSEBUTTONUP:
            if looking:
                pass
            else:
                ePoint = Point(mouse_x, mouse_y)
                pointing = False

        if event.type == pygame.KEYUP and event.dict["unicode"] == "e":
            looking = not looking # use e to toggle between looking and placing points

    keys = pygame.key.get_pressed()
#input ------------------------------------------------------------------------------------------#
    if keys[pygame.K_ESCAPE]:
        run = False

    # actually deleting points
    if keys[pygame.K_DELETE] and del_cooldown and bool(len(Point.points)):
        Point.points[-1].begone()
        del_cooldown = False
    elif keys[pygame.K_DELETE]:
        del_cooldown = False
    else: del_cooldown = True

    # moving player
    if keys[pygame.K_w]:
        pl.move_forward()
    if keys[pygame.K_a]:
        pl.move_left()
    if keys[pygame.K_s]:
        pl.move_backward()
    if keys[pygame.K_d]:
        pl.move_right()

    # looking around
    if keys[pygame.K_LEFT]:
        pl.d -= 5
    if keys[pygame.K_RIGHT]:
        pl.d += 5
    if pl.d > 360:
        pl.d -= 360
    elif pl.d < 0:
        pl.d += 360

    # place a tree at mouse position if space is pressed
    if keys[pygame.K_SPACE]:
        Tree(mouse_x, mouse_y)

    # reposition the mouse if the player is looking so they don't have to stop looking to reset the mouse position
    if looking:
        pygame.mouse.set_pos(win_width / 2, win_height / 2)

pygame.quit()
