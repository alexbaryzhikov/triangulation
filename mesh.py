"""

Mesh: points, edges.

"""

import pygame
import numpy as np
import math
from   config import *
import config as G
from   delaunay import delaunay


class Mesh:
    """Mesh class. Holds points, edges, and methods for drawing them."""

    def __init__(self):
        np.random.seed(RND_SEED)
        self.points     = None
        self.edges      = None
        self.font_size  = 16
        self.font       = pygame.font.SysFont('Liberation Mono', self.font_size)
        self.cross      = draw_cross()

    def generate(self):
        if GEN_MODE == 'GRID':
            self.points = gen_grid(G.screen_w, G.screen_h, GRID_CELLS)
        elif GEN_MODE == 'CRCL':
            self.points = gen_circle(G.screen_w, G.screen_h, CRCL_POINTS)
        elif GEN_MODE == 'CRCL_I':
            self.points = gen_circle_i(G.screen_w, G.screen_h, CRCL_POINTS)
        else:
            self.points = gen_random(G.screen_w, G.screen_h, RND_POINTS)

        self.edges  = delaunay(self.points)
        self.draw(G.screen)

    def draw(self, screen):
        
        screen.fill(BG_COLOR)
        d = self.cross.get_rect().width // 2

        # draw edges
        for e in self.edges:
            pygame.draw.line(screen, LINE_COLOR, e.org, e.dest)

        # draw points
        for p in self.points:
            point_rect = pygame.Rect(p[0] - d, p[1] - d, p[0] + d, p[1] + d)
            screen.blit(self.cross, point_rect)
            if DRAW_LABELS:
                label = '({}, {})'.format(p[0], p[1])
                text = self.font.render(label, 0, TEXT_COLOR)
                screen.blit(text, (p[0] + 5, p[1] - self.font_size))
        
        pygame.display.flip()


# -----------------------------------------------------------------
# Mesh auxiliary methods


def draw_cross():
    """Returns surface with cross."""
    canvas = pygame.Surface((CROSS_SIZE*2 + 1, CROSS_SIZE*2 + 1))
    canvas.fill(COLOR_KEY)
    canvas.set_colorkey(COLOR_KEY)
    pygame.draw.line(canvas, CROSS_COLOR, [0, CROSS_SIZE], [CROSS_SIZE*2 + 1, CROSS_SIZE])
    pygame.draw.line(canvas, CROSS_COLOR, [CROSS_SIZE, 0], [CROSS_SIZE, CROSS_SIZE*2 + 1])
    return canvas


def gen_random(w, h, n):
    """Returns an array of randomly generated points.
       w, h     width, height
       n        number of points"""
    points_x = np.random.randint(0, w, n)
    points_y = np.random.randint(0, h, n)
    return np.asarray(list(zip(points_x, points_y)))

def gen_grid(w, h, n):
    """Returns grid-like array of points.
       w, h     width, height
       n        number of cells along axis"""
    points_x = np.linspace(50, w-50, n+1, dtype=np.int64)
    points_y = np.linspace(50, h-50, n+1, dtype=np.int64)
    return np.asarray(list((i, j) for i in points_x for j in points_y))

def gen_circle(w, h, n):
    """Returns circular array of points. Float coordinates.
       w, h     width, height of the screen
       n        number of points"""
    rads = np.linspace(0, 2*math.pi, n+1)
    cx, cy = w // 2, h // 2
    r = min(cx, cy) - 50
    return np.asarray(list((cx + r * math.cos(i), cy + r * math.sin(i)) for i in rads)[:-1])

def gen_circle_i(w, h, n):
    """Returns circular array of points. Integer coordinates.
       w, h     width, height of the screen
       n        number of points"""
    rads = np.linspace(0, 2*math.pi, n+1)
    cx, cy = w // 2, h // 2
    r = min(cx, cy) - 50
    return np.asarray(list((int(cx + r * math.cos(i)), int(cy + r * math.sin(i))) for i in rads)[:-1])
