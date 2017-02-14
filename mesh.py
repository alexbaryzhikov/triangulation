import  pygame
import  numpy as np
import  math
from    config import *
import  config as G

#=======================================================================
#
# Mesh
#
# Triangulation class, holds points as numpy array and triangles graph.
#
#=======================================================================
class Mesh:

    #--------------------------------------------
    # __init__
    #--------------------------------------------
    def __init__(self):
        ## data
        self.points     = None
        self.p_ids      = None
        self.tris       = None
        self.ghosts     = None
        self.state      = 0
        ## visuals
        self.font_size  = 16
        self.font       = pygame.font.SysFont('Liberation Mono', self.font_size)
        self.cross      = self.draw_cross()

    #--------------------------------------------
    # generate_points
    #--------------------------------------------
    def generate_points(self):
        points_x = np.random.randint(0, G.screen_w, NUM_POINTS)
        points_y = np.random.randint(0, G.screen_h, NUM_POINTS)
        return np.asarray(list(zip(points_x, points_y)))

    #--------------------------------------------
    # update
    #--------------------------------------------
    def update(self):
        if self.state < 0: return

        ## initialize
        if self.state == 0:
            self.points = self.generate_points()
            self.p_ids  = [i for i in range(self.points.shape[0])]
            self.tris   = []
            self.ghosts = []

            ## sort points by x coordinate, y is a tiebreaker
            self.points.view('i8, i8').sort(order=['f0', 'f1'], axis=0)

            ## remove duplicates
            dupes = []
            for i in range(self.points.shape[0]-1):
                if  self.points[i][0] == self.points[i+1][0] \
                and self.points[i][1] == self.points[i+1][1]:
                    dupes.append(i+1)
            if dupes:
                self.points = np.delete(self.points, dupes, 0)
                self.p_ids = [i for i in range(self.points.shape[0])]

        elif self.state == 1:
            Triangle([0, 1, 2])

        elif self.state == 2:
            Triangle([1, 6, 2])
        
        elif self.state == 3:
            t0, t1 = self.tris[0], self.tris[1]
            t0.append(0, t1, 1)

        elif self.state == 4:
            self.tris[0].separate()

            # ## border walk
            # tmp = self.ghosts[0]
            # print(tmp.points)
            # tmp = tmp.adjacent[0]
            # print(tmp.points)
            # tmp = tmp.adjacent[0]
            # print(tmp.points)
            # tmp = tmp.adjacent[0]
            # print(tmp.points)
            # tmp = tmp.adjacent[0]
            # print(tmp.points)


            ## go to the final state
            self.state = -1

        # ## subdivide points to small subsets and triangulate
        # elif self.state == 2:
        #     for t in subdivide(self.p_ids):
        #         self.tris.append(Triangle(t))
        #     self.state = -1

        if self.state >= 0: self.state += 1

    #--------------------------------------------
    # draw
    #--------------------------------------------
    def draw(self, screen):
        if self.state == -2: return
        if self.state == -1: self.state = -2
        
        screen.fill(BG_COLOR)
        d = self.cross.get_rect().width // 2

        ## points
        for p, i in zip(self.points, self.p_ids):
            point_rect = pygame.Rect(p[0] - d, p[1] - d, p[0] + d, p[1] + d)
            screen.blit(self.cross, point_rect)
            text = self.font.render(str(i), 0, TEXT_COLOR)
            screen.blit(text, (p[0] + 5, p[1] - self.font_size))
        
        ## ghosts
        for t in self.ghosts:
            p0 = t.points[0]
            p1 = t.points[1]
            pa = angle_to(self.points[p0], self.points[p1]) - math.pi/2
            p2 = [(self.points[p0][0] + self.points[p1][0])//2 + 30*math.cos(pa),
                  (self.points[p0][1] + self.points[p1][1])//2 + 30*math.sin(pa)]
            pygame.draw.line(screen, LINE_COLOR, self.points[p0], self.points[p1])
            pygame.draw.line(screen, GHOST_COLOR, self.points[p0], p2)
            pygame.draw.line(screen, GHOST_COLOR, self.points[p1], p2)

        ## triangles
        for t in self.tris:
            G.log_file.write(str(t))
            p0 = t.points[0]
            p1 = t.points[1]
            p2 = t.points[2]
            pygame.draw.line(screen, LINE_COLOR, self.points[p0], self.points[p1])
            pygame.draw.line(screen, LINE_COLOR, self.points[p0], self.points[p2])
            pygame.draw.line(screen, LINE_COLOR, self.points[p1], self.points[p2])
        
        if self.tris: G.log_file.write('\n')

    #--------------------------------------------
    # draw_cross
    #--------------------------------------------
    def draw_cross(self):
        canvas = pygame.Surface((CROSS_SIZE*2 + 1, CROSS_SIZE*2 + 1))
        canvas.fill(COLOR_KEY)
        canvas.set_colorkey(COLOR_KEY)
        pygame.draw.line(canvas, CROSS_COLOR, [0, CROSS_SIZE], [CROSS_SIZE*2 + 1, CROSS_SIZE])
        pygame.draw.line(canvas, CROSS_COLOR, [CROSS_SIZE, 0], [CROSS_SIZE, CROSS_SIZE*2 + 1])
        return canvas

#=======================================================================
#
# Triangle
#
# Truangular data structure: 3 vertices and 3 links to adjacent triangles.
# Border is surrounded by 'ghost' triangles, single edge is represented by
# two adjacent ghost triangles.
#
#=======================================================================
class Triangle:

    #--------------------------------------------
    # __init__
    #--------------------------------------------
    def __init__(self, points):
        ## data
        self.points     = self.reorder(points)
        self.adjacent   = [None, None, None]
        if not self.is_ghost():
            G.mesh.tris.append(self)
            self.separate()
        else:
            G.mesh.ghosts.append(self)

    #--------------------------------------------
    # reorder
    #
    # Reorder points so that the first point is the lowest one in point ordering,
    # and vertex two is clockwise from vertex one and vertex three is clockwise from
    # vertex two. If it's a ghost triangle, then assign vertex three to None.
    #--------------------------------------------
    def reorder(self, points):
        res = points[:]
        if len(res) < 3:
            res.append(None)
        else:
            ang_p1 = angle_to(G.mesh.points[res[0]], G.mesh.points[res[1]])
            ang_p2 = angle_to(G.mesh.points[res[0]], G.mesh.points[res[2]])
            if ang_p2 < ang_p1:
                res[1], res[2] = res[2], res[1]
        return res

    #--------------------------------------------
    # is_ghost
    #--------------------------------------------
    def is_ghost(self):
        return self.points[2] is None

    #--------------------------------------------
    # append
    #
    # a_edg = shared edge of this triangle
    # b_tri = target triangle
    # b_edg = shared edge of target triangle
    #--------------------------------------------
    def append(self, a_edg, b_tri, b_edg):
        ## check if append is legit
        if not (self.adjacent[a_edg] and self.adjacent[a_edg].is_ghost() \
        and b_tri.adjacent[b_edg] and b_tri.adjacent[b_edg].is_ghost()):
            G.log_file.write('Error: cannot append {} (edge {} -> {}) to {} \
                (edge {} -> {}).\n'.format(self.points, a_edg, self.adjacent[a_edg].points, \
                b_tri.points, b_edg, b_tri.adjacent[b_edg].points))
            return

        ## merge across the shared edge
        self.adjacent[a_edg].delete()
        self.adjacent[a_edg] = b_tri
        b_tri.adjacent[b_edg].delete()
        b_tri.adjacent[b_edg] = self

        ## link adjacent ghosts around A of the shared edge
        t_prev = b_tri
        t_next = b_tri.adjacent[self.next_idx(b_edg)]
        while not (t_next.is_ghost() or t_next == self):
            dir = t_next.adjacent.index(t_prev) # where we came from
            dir = self.next_idx(dir)            # where we go next
            t_prev, t_next = t_next, t_next.adjacent[dir]
        if t_next.is_ghost():
            ghost = self.adjacent[self.prev_idx(a_edg)]
            ghost.adjacent[0] = t_next
            t_next.adjacent[1] = ghost

        ## link adjacent ghosts around B of the shared edge
        t_prev = b_tri
        t_next = b_tri.adjacent[self.prev_idx(b_edg)]
        while not (t_next.is_ghost() or t_next == self):
            dir = t_next.adjacent.index(t_prev) # where we came from
            dir = self.prev_idx(dir)            # where we go next
            t_prev, t_next = t_next, t_next.adjacent[dir]
        if t_next.is_ghost():
            ghost = self.adjacent[self.next_idx(a_edg)]
            ghost.adjacent[1] = t_next
            t_next.adjacent[0] = ghost

    #--------------------------------------------
    # separate
    #
    # Separate triangle from all neighbours and replace broken links with ghosts.
    #
    # v = index of the vertex, opposite to shared edge
    # t = appended triangle
    #--------------------------------------------
    def separate(self):
        edge_indices    = [[1, 2], [2, 0], [0, 1]]
        neighbors       = []
        
        ## memorize neighbors and replace with ghosts
        for i in range(3):
            if self.adjacent[i] and not self.adjacent[i].is_ghost():
                neighbors.append(self.adjacent[i])

            if not (self.adjacent[i] and self.adjacent[i].is_ghost()):
                a, b = edge_indices[i]
                self.adjacent[i] = Triangle([self.points[a], self.points[b]])
        
        ## interconnect own ghosts
        for i in range(3):
            a, b = edge_indices[i]
            self.adjacent[i].adjacent[0] = self.adjacent[a]
            self.adjacent[i].adjacent[1] = self.adjacent[b]
            self.adjacent[i].adjacent[2] = self
        
        ## create new ghosts for neighbors
        new_ghosts = {}
        for t in neighbors:
            i               = t.adjacent.index(self)
            new_ghosts[t]   = i
            a, b            = edge_indices[i]
            t.adjacent[i]   = Triangle([t.points[a], t.points[b]])

        ## connect neighbors' ghosts
        for t in neighbors:
            i       = new_ghosts[t]
            a, b    = edge_indices[i]

            ## get adjacent ghosts
            t_prev = t
            t_next = t.adjacent[a]
            while not t_next.is_ghost():
                dir = t_next.adjacent.index(t_prev) # where we came from
                dir = self.next_idx(dir)            # where we go next
                t_prev, t_next = t_next, t_next.adjacent[dir]
            cw_ghost = t_next

            t_prev = t
            t_next = t.adjacent[b]
            while not t_next.is_ghost():
                dir = t_next.adjacent.index(t_prev) # where we came from
                dir = self.prev_idx(dir)            # where we go next
                t_prev, t_next = t_next, t_next.adjacent[dir]
            ccw_ghost = t_next

            ## link
            t.adjacent[i].adjacent[0]   = cw_ghost
            t.adjacent[i].adjacent[1]   = ccw_ghost
            t.adjacent[i].adjacent[2]   = t
            cw_ghost.adjacent[1]        = t.adjacent[i]
            ccw_ghost.adjacent[0]       = t.adjacent[i]

    #--------------------------------------------
    # delete (Only for ghosts atm!)
    #
    # Delete current triangle from mesh list.
    #--------------------------------------------
    def delete(self):
        if self.is_ghost():
            G.mesh.ghosts.remove(self)

    #--------------------------------------------
    # next_idx
    #
    # 0 -> 1 -> 2 -> 0
    #--------------------------------------------
    def next_idx(self, i):
        i += 1
        if i > 2: i = 0
        return i

    #--------------------------------------------
    # prev_idx
    #
    # 0 -> 2 -> 1 -> 0
    #--------------------------------------------
    def prev_idx(self, i):
        i -= 1
        if i < 0: i = 2
        return i

    def __str__(self):
        return '{} -> {}, {}, {}\n'.format(self.points, \
            *[self.adjacent[i].points for i in range(3)])


#=======================================================================
#
# Triangulation routines
#
#=======================================================================

#--------------------------------------------
# subdivide
#
# Return a list of subsets not larger that 3.
#--------------------------------------------
def subdivide(a):
    if len(a) < 4: return [a]
    res = []
    i = (len(a) + 1)//2
    res.extend(subdivide(a[:i]))
    res.extend(subdivide(a[i:]))
    return res

#--------------------------------------------
# merge
#
# Merge two halves of triangulation.
#--------------------------------------------
def merge(a):
    ## pick base LR-edge
    pass


#=======================================================================
#
# Utilities
#
#=======================================================================

#--------------------------------------------
# angle_to
#--------------------------------------------
def angle_to(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    return math.atan2(dy, dx)

#--------------------------------------------
# cw_angle
#
# Return CW angle.
#--------------------------------------------
def cw_angle(a0, a1):
    if a0 == a1: return 0
    if a0 < a1: return a1 - a0
    return math.pi*2 + a1 - a0

#--------------------------------------------
# ccw_angle
#
# Return positive CCW angle.
#--------------------------------------------
def ccw_angle(a0, a1):
    if a0 == a1: return 0
    if a1 < a0: return a0 - a1
    return math.pi*2 + a0 - a1

#--------------------------------------------
# orientation
#
# Does C lie on, to the left of, or to the right of AB?
# Return -1 (left), 0 (on), 1 (right)
#--------------------------------------------
def orientation(a, b, c):
    m = np.asarray([ [a[0]-c[0], a[1]-c[1]],
                     [b[0]-c[0], b[1]-c[1]] ])
    det = np.linalg.det(m)
    if det < 0: return 1    # to the right
    elif det > 0: return -1 # to the left
    return 0                # on the line

#--------------------------------------------
# in_circle
#
# Does D lie on, inside or outside of circumcircle ABC?
# Return -1 (inside), 0 (on), 1 (outside)
#--------------------------------------------
def in_circle(a, b, c, d):
    adx, ady = a[0]-d[0], a[1]-d[1]
    bdx, bdy = b[0]-d[0], b[1]-d[1]
    cdx, cdy = c[0]-d[0], c[1]-d[1]
    m = np.asarray([ [adx, ady, adx**2 + ady**2],
                     [bdx, bdy, bdx**2 + bdy**2],
                     [cdx, cdy, cdx**2 + cdy**2] ])
    det = np.linalg.det(m)
    if det < 0: return -1   # inside
    elif det > 0: return 1  # outside
    return 0                # on the circle
