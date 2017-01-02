from    math import atan2
import  config as G

'''
=============================
Triangle
=============================
'''
class Triangle:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self, points):
        ## data
        self.points     = self.reorder(points)
        self.adjacent   = [None, None, None]

    '''
    =============================
    reorder
    =============================
    '''
    def reorder(self, points):
        '''Reorder points so that the first point is the lowest one in point ordering,
        and vertex two is clockwise from vertex one and vertex three is clockwise from
        vertex two. If there're only two vertices, then assign vertex three to 'None'.'''
        res = points[:]
        if len(res) < 3:
            res.append(None)
        else:
            dy      = G.tris.points[res[1]][1] - G.tris.points[res[0]][1]
            dx      = G.tris.points[res[1]][0] - G.tris.points[res[0]][0]
            ang_p1  = atan2(dy, dx)
            dy      = G.tris.points[res[2]][1] - G.tris.points[res[0]][1]
            dx      = G.tris.points[res[2]][0] - G.tris.points[res[0]][0]
            ang_p2  = atan2(dy, dx)
            if ang_p2 < ang_p1:
                res[1], res[2] = res[2], res[1]
        return res