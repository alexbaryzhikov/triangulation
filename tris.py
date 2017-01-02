import  pygame
import  numpy as np
from    config import *
import  config as G
from    triangle import Triangle

'''
=============================
Tris
=============================
'''
class Tris:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        ## data
        self.points     = None
        self.p_indexes  = None
        self.tris       = None
        self.state      = 0
        ## visuals
        self.font_size  = 20
        self.font       = pygame.font.SysFont('Liberation Mono', self.font_size)
        self.cross      = self.draw_cross()

    '''
    =============================
    generate_points
    =============================
    '''
    def generate_points(self):
        points_x = np.random.randint(0, G.screen_w, NUM_POINTS)
        points_y = np.random.randint(0, G.screen_h, NUM_POINTS)
        return np.asarray(list(zip(points_x, points_y)))

    '''
    =============================
    update
    =============================
    '''
    def update(self):
        if self.state < 0: return

        ## initialize
        if self.state == 0:
            self.points = self.generate_points()
            self.p_indexes = [i for i in range(self.points.shape[0])]
            self.tris = []

        ## sort points by x coordinate, y is a tiebreaker
        elif self.state == 1:
            self.points.view('i8, i8').sort(order=['f0', 'f1'], axis=0)

        ## subdivide points to small subsets and triangulate
        elif self.state == 2:
            for t in self.subdivide(self.p_indexes):
                self.tris.append(Triangle(t))
            self.state = -1

        if not self.state < 0: self.state += 1

    '''
    =============================
    draw
    =============================
    '''
    def draw(self, screen):
        if self.state == -2: return
        if self.state == -1: self.state = -2
        
        screen.fill(BG_COLOR)
        cross_offset = self.cross.get_rect().width // 2

        ## points
        for p, i in zip(self.points, self.p_indexes):
            point_rect = pygame.Rect(p[0]-cross_offset, p[1]-cross_offset, p[0]+cross_offset, p[1]+cross_offset)
            screen.blit(self.cross, point_rect)
            text = self.font.render(str(i), 0, TEXT_COLOR)
            screen.blit(text, (p[0] + 5, p[1] - self.font_size))
        
        ## triangles
        for t in self.tris:
            print(t.points)
            p0 = self.points[t.points[0]]
            p1 = self.points[t.points[1]]
            pygame.draw.line(screen, LINE_COLOR, p0, p1)
            if not t.points[2] is None:
                p2 = self.points[t.points[2]]
                pygame.draw.line(screen, LINE_COLOR, p1, p2)
                pygame.draw.line(screen, LINE_COLOR, p2, p0)
        
        if self.tris: print()

    '''
    =============================
    draw_cross
    =============================
    '''
    def draw_cross(self):
        canvas      = pygame.Surface((CROSS_SIZE*2 + 1, CROSS_SIZE*2 + 1))
        canvas.fill(COLOR_KEY)
        canvas.set_colorkey(COLOR_KEY)
        pygame.draw.line(canvas, CROSS_COLOR, [0, CROSS_SIZE], [CROSS_SIZE*2 + 1, CROSS_SIZE])
        pygame.draw.line(canvas, CROSS_COLOR, [CROSS_SIZE, 0], [CROSS_SIZE, CROSS_SIZE*2 + 1])
        return canvas

    '''
    =============================
    subdivide
    =============================
    '''
    def subdivide(self, a):
        '''Returns a list of subsets not larger that 3.'''
        if len(a) < 4: return [a]
        res = []
        i = (len(a) + 1)//2
        res.extend(self.subdivide(a[:i]))
        res.extend(self.subdivide(a[i:]))
        return res

