import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import os

# Game constants
SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1024
GROUND_HEIGHT = 200
BIRD_SIZE = 64
PIPE_WIDTH = 104
PIPE_DEPTH = 52
PIPE_GAP = 200
FPS = 60

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2
        self.z = 0
        self.vel = 0
        # Positive y is upward in the OpenGL view, so gravity should be
        # negative to make the bird fall downward. Likewise, the flap power
        # should be positive to move the bird upward when the player flaps.
        self.gravity = -0.5
        self.flap_power = 7
        self.orientation = 0
        self.wing_phase = 0

    def update(self):
        self.vel += self.gravity
        self.y += self.vel
        self.wing_phase = (self.wing_phase + 0.3) % (2 * 3.14159)

    def flap(self):
        self.vel = self.flap_power

    def get_aabb(self):
        return (self.x, self.y, self.z, BIRD_SIZE, BIRD_SIZE, BIRD_SIZE)

class PipeBox:
    def __init__(self, x, y, h):
        self.x = x
        self.y = y
        self.z = 0
        self.w = PIPE_WIDTH
        self.h = h
        self.d = PIPE_DEPTH

    def move(self, dx):
        self.x += dx

    def get_aabb(self):
        return (self.x, self.y, self.z, self.w, self.h, self.d)


def create_pipe_pair():
    gap_y = random.randint(50, SCREEN_HEIGHT - GROUND_HEIGHT - 50 - PIPE_GAP)
    top = PipeBox(SCREEN_WIDTH, 0, gap_y)
    bottom_height = SCREEN_HEIGHT - gap_y - PIPE_GAP - GROUND_HEIGHT
    bottom = PipeBox(SCREEN_WIDTH, gap_y + PIPE_GAP, bottom_height)
    return top, bottom


def aabb_intersect(a, b):
    ax, ay, az, aw, ah, ad = a
    bx, by, bz, bw, bh, bd = b
    return (
        ax < bx + bw and ax + aw > bx and
        ay < by + bh and ay + ah > by and
        az < bz + bd and az + ad > bz
    )


def draw_box(box, color):
    x, y, z, w, h, d = box
    r, g, b = [c / 255.0 for c in color]
    glColor3f(r, g, b)
    glPushMatrix()
    glTranslatef(x, y, -z - 200)
    glBegin(GL_QUADS)
    # Front
    glVertex3f(0, 0, 0)
    glVertex3f(w, 0, 0)
    glVertex3f(w, h, 0)
    glVertex3f(0, h, 0)
    # Back
    glVertex3f(0, 0, -d)
    glVertex3f(w, 0, -d)
    glVertex3f(w, h, -d)
    glVertex3f(0, h, -d)
    # Left
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, -d)
    glVertex3f(0, h, -d)
    glVertex3f(0, h, 0)
    # Right
    glVertex3f(w, 0, 0)
    glVertex3f(w, 0, -d)
    glVertex3f(w, h, -d)
    glVertex3f(w, h, 0)
    # Top
    glVertex3f(0, h, 0)
    glVertex3f(w, h, 0)
    glVertex3f(w, h, -d)
    glVertex3f(0, h, -d)
    # Bottom
    glVertex3f(0, 0, 0)
    glVertex3f(w, 0, 0)
    glVertex3f(w, 0, -d)
    glVertex3f(0, 0, -d)
    glEnd()
    glPopMatrix()


def draw_bird(bird):
    # Body
    draw_box(bird.get_aabb(), (255, 255, 0))

    wing_span = BIRD_SIZE
    wing_width = BIRD_SIZE / 4
    angle = math.sin(bird.wing_phase) * 30
    glColor3f(1, 0, 0)

    # Left wing
    glPushMatrix()
    glTranslatef(bird.x, bird.y + BIRD_SIZE / 2, -bird.z - 200)
    glRotatef(angle, 0, 0, 1)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(-wing_span, 0, 0)
    glVertex3f(0, wing_width, 0)
    glEnd()
    glPopMatrix()

    # Right wing
    glPushMatrix()
    glTranslatef(bird.x + BIRD_SIZE, bird.y + BIRD_SIZE / 2, -bird.z - 200)
    glRotatef(-angle, 0, 0, 1)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(wing_span, 0, 0)
    glVertex3f(0, wing_width, 0)
    glEnd()
    glPopMatrix()


def init_gl():
    glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)


def main():
    pygame.init()
    try:
        pygame.mixer.init()
        hit_sound = pygame.mixer.Sound('hit.wav') if os.path.exists('hit.wav') else None
    except pygame.error:
        hit_sound = None
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    clock = pygame.time.Clock()
    init_gl()

    bird = Bird()
    pipes = []
    pipe_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.flap()

        bird.update()
        pipe_timer += 1
        if pipe_timer > 90:
            pipes.append(create_pipe_pair())
            pipe_timer = 0

        for pipe_pair in pipes:
            pipe_pair[0].move(-2)
            pipe_pair[1].move(-2)

        pipes = [p for p in pipes if p[0].x + p[0].w > 0]

        # Collision detection using 3D bounding boxes
        bird_box = bird.get_aabb()
        for top, bottom in pipes:
            if aabb_intersect(bird_box, top.get_aabb()) or aabb_intersect(bird_box, bottom.get_aabb()):
                if hit_sound:
                    hit_sound.play()
                running = False
        if bird.y + BIRD_SIZE > SCREEN_HEIGHT - GROUND_HEIGHT:
            if hit_sound:
                hit_sound.play()
            running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(-bird.x, -SCREEN_HEIGHT/2, -300)

        for top, bottom in pipes:
            draw_box(top.get_aabb(), (0, 255, 0))
            draw_box(bottom.get_aabb(), (0, 255, 0))

        draw_bird(bird)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
