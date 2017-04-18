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
