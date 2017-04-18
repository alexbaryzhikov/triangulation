"""

Delaunay Triangulation. 

Given a set of points on a plane, compute DT using divide-and-conquer
alogorithm.

"""

import pygame
from   pygame.locals import *
from   config import *
import config as G
import time
from   mesh import Mesh


def main():
    pygame.init()
    pygame.display.set_caption('Delaunay')
    G.screen_w = SCREEN_W
    G.screen_h = SCREEN_H
    G.screen_mode = SCREEN_MODE
    G.screen = pygame.display.set_mode([G.screen_w, G.screen_h], G.screen_mode)
    G.screen.fill(BG_COLOR)
    G.background = G.screen.copy()

    G.mesh = Mesh()
    G.mesh.generate()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if event.__dict__['key'] == 32:         # space
                    G.mesh.generate()
        time.sleep(0.1)


if __name__ == '__main__': main()
