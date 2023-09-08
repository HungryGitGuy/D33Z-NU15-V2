import pygame, math

pygame.init()

win = pygame.display.set_mode((1300, 700))
win_width = win.get_width()
win_height = win.get_height()


RENDERLIST = []
def sort_by_i4(i):
    return i[3]


class Player:
    def __init__(self, x, y, direction=0, fov=90):
        """
        a class representing the player, the camera, ant the renderer
        :param x: position along the x axis
        :param y: position along the y axis
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


    def debug_draw(self):
        pygame.draw.rect(win, (0, 0, 255), (self.p.x - 5, self.p.y - 5, 10, 10))
        pygame.draw.line(win, (0, 0, 255), (self.p.x, self.p.y), (self.p.x + (math.cos(math.radians(self.d)) * 30), self.p.y + (math.sin(math.radians(self.d)) * 30)), 1)

    # renderer+camera functions below

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

        # "CULL THE WEAK!!!" - John Seed I think
        L = round(self.d - (self.fov / 2))
        R = round(self.d + (self.fov / 2))
        L %= 360
        R %= 360
        angle %= 360

        if L < R:
            if angle < L or angle > R:
                return
#
        elif angle < L and angle > R:
            return

        height = (35000 / distance) + 350
        y = round(-350 - height) + 1000
        height -= y
        c = (255, 0, 255)

        pygame.draw.rect(win, c, (draw_x, y, 10, height))
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
    points = []
    def __init__(self, x, y):
        """
        A base class for anything that needs to be represented by a point in space.
        :param x: position along the x axis
        :param y: position along the y axis
        :param col: colour (r, g, b)
        :return:
        """
        self.p = pygame.Vector2(x, y)
        self.col = col = (255, 255, 0)
        self.lpos = len(Point.points) - 1

        Point.points.append(self)

    def begone(self):
        try:
            Point.points.pop(self.lpos)
        except Exception:
            Point.points = []

    def debug_draw(self, scale=3):
        pygame.draw.rect(win, self.col, (self.p.x - (scale * 0.5), self.p.y - (scale * 0.5), scale, scale))

    def get_angle(self, pos):
        pos = pygame.Vector2(pos)
        angle = self.p.angle_to(pos) + 180

        return angle


class Tree:
    trees = []
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.p = pygame.Vector2(x, y)
        self.img = pygame.image.load(("assets\\Tree1.png")).convert()
        self.hp = 100
        #self.rect = pygame.rect.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        Tree.trees.append(self)

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

        # "CULL THE WEAK!!!" - John Seed I think (this is culling in case you couldn't tell)
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
        dimensions = self.get_view_dimensions()
        try:
            i_copy = self.img.copy()
            im = pygame.transform.scale(i_copy, (dimensions[3], dimensions[2]))
            im.set_colorkey((255, 255, 255))
            RENDERLIST.append((im, dimensions[0] - (im.get_width() / 2), dimensions[1], dimensions[4]))
            #win.blit(im, (dimensions[0] - (im.get_width() / 2), dimensions[1]))
        except Exception as e: pass
            #print("214", e)


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
    if len(Point.points) > 0:
        for p in Point.points:
            pl.draw_point(p)
    if len(Tree.trees) > 0:
        for t in Tree.trees:
            t.draw()
    if len(RENDERLIST) > 0:
        RENDERLIST.sort(key=sort_by_i4, reverse=True) # fix
        for i in RENDERLIST:
            win.blit(i[0], (i[1], i[2]))

    # HUD render
    win.blit(HUD.weapon, (0, 0))

    # window update
    pygame.display.update()

    # render cleanup
    RENDERLIST.clear()

    # debug

    #pl.debug_draw()


# mainloop -----------------------------------------------------------------------------------------#
run = True
pointing = False
clock = pygame.time.Clock()

# default point, as of 7/16/2023, 292 lines, this is the only point that works properly and any changes to the points list will irreversibly break it until restart
bPoint = Point(0, 0)

mouse_pos = pygame.mouse.get_pos()
mouse_x = mouse_pos[0]
mouse_y = mouse_pos[1]

del_cooldown = False
looking = False
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
            looking = not looking

    keys = pygame.key.get_pressed()
#input ------------------------------------------------------------------------------------------#
    if keys[pygame.K_ESCAPE]:
        run = False

    if keys[pygame.K_DELETE] and del_cooldown and bool(len(Point.points)):
        Point.points[-1].begone()
        del_cooldown = False
    elif keys[pygame.K_DELETE]:
        del_cooldown = False
    else: del_cooldown = True

    if keys[pygame.K_w]:
        pl.move_forward()
    if keys[pygame.K_a]:
        pl.move_left()
    if keys[pygame.K_s]:
        pl.move_backward()
    if keys[pygame.K_d]:
        pl.move_right()

    if keys[pygame.K_LEFT]:
        pl.d -= 5
    if keys[pygame.K_RIGHT]:
        pl.d += 5
    if pl.d > 360:
        pl.d -= 360
    elif pl.d < 0:
        pl.d += 360

    if keys[pygame.K_SPACE]:
        Tree(mouse_x, mouse_y)

    if looking:
        pygame.mouse.set_pos(win_width / 2, win_height / 2)

pygame.quit()
