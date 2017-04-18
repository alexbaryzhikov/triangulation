"""

The divide-and-conquer algorithm for computing Delaunay triangulation of a set of points.

"""

import numpy as np
import math

edges = [] # module-wide container for edges


# -----------------------------------------------------------------
# Interface method, that is supposed to be exported.


def delaunay(S):
    """Assumes S is a list of points of form (x, y).
    Returns a list of edges that form a Delaunay triangulation of S."""
    global edges
    edges = []
    if type(S) != np.ndarray:
        S = np.asarray(S)
    S = p_remdup(p_sort(S))  # sort and remove duplicate points
    triangulate(S)
    return edges


# -----------------------------------------------------------------
# Quad edge data structure.


class Edge:
    """A directed edge: org -> dest.
    When traversing edge ring: Next is CCW, Prev is CW."""

    def __init__(self, org, dest):
        self.org   = org
        self.dest  = dest
        self.onext = None
        self.oprev = None
        self.dnext = None
        self.dprev = None
        self.sym   = None    # symmetrical counterpart of this edge
        self.data  = None    # can store anyting (e.g. tag), for external use

    def set_org(self, p):
        self.org = p
        self.sym.dest = p

    def set_dest(self, p):
        self.dest = p
        self.sym.org = p

    def set_onext(self, e):
        self.onext = e
        self.sym.dnext = e.sym

    def set_oprev(self, e):
        self.oprev = e
        self.sym.dprev = e.sym

    def set_dnext(self, e):
        self.dnext = e
        self.sym.onext = e.sym

    def set_dprev(self, e):
        self.dprev = e
        self.sym.oprev = e.sym

    def __str__(self):
        s = '[' + str(self.org) + ', ' + str(self.dest) + ']'
        if self.data is None:
            return s
        else:
            return s + ' ' + str(self.data)


# -----------------------------------------------------------------
# Main triangulation routine


def triangulate(S):
    """Computes the Delaunay triangulation of a point set S and returns two edges, le and re,
    which are the counterclockwise convex hull edge out of the leftmost vertex and the clockwise
    convex hull edge out of the rightmost vertex, respectively."""

    if len(S) == 2:
        a = make_edge(S[0], S[1])
        return a, a.sym

    elif len(S) == 3:
        # Create edges a connecting p1 to p2 and b connecting p2 to p3.
        p1, p2, p3 = S[0], S[1], S[2]
        a = make_edge(p1, p2)
        b = make_edge(p2, p3)
        splice(a.sym, b)

        # Close the triangle.
        if right_of(p3, a):
            connect(b, a)
            return a, b.sym
        elif left_of(p3, a):
            c = connect(b, a)
            return c.sym, c
        else:  # the three points are collinear
            return a, b.sym

    else:
        # Recursively subdivide S.
        m = (len(S) + 1) // 2
        L, R = S[:m], S[m:]
        ldo, ldi = triangulate(L)
        rdi, rdo = triangulate(R)

        # Compute the upper common tangent of L and R.
        while True:
            if right_of(rdi.org, ldi):
                ldi = ldi.sym.onext
            elif left_of(ldi.org, rdi):
                rdi = rdi.sym.oprev
            else:
                break

        # Create a first cross edge rbase from rdi.org to ldi.org.
        rbase = connect(ldi.sym, rdi)

        # Adjust ldo and rdo
        if p_coinside(ldi.org, ldo.org):
            ldo = rbase
        if p_coinside(rdi.org, rdo.org):
            rdo = rbase.sym

        # Merge.
        while True:
            # Locate the first R and L points to be encountered by the diving bubble.
            rcand, lcand = rbase.sym.onext, rbase.oprev
            # If both lcand and rcand are invalid, then rbase is the lower common tangent.
            v_rcand, v_lcand = right_of(rcand.dest, rbase), right_of(lcand.dest, rbase)
            if not (v_rcand or v_lcand):
                break
            # Delete R edges out of rbase.dest that fail the circle test.
            if v_rcand:
                while right_of(rcand.onext.dest, rbase) and \
                      in_circle(rbase.dest, rbase.org, rcand.dest, rcand.onext.dest) == 1:
                    t = rcand.onext
                    delete_edge(rcand)
                    rcand = t
            # Symmetrically, delete L edges.
            if v_lcand:
                while right_of(lcand.oprev.dest, rbase) and \
                      in_circle(rbase.dest, rbase.org, lcand.dest, lcand.oprev.dest) == 1:
                    t = lcand.oprev
                    delete_edge(lcand)
                    lcand = t
            # The next cross edge is to be connected to either lcand.dest or rcand.dest.
            # If both are valid, then choose the appropriate one using the in_circle test.
            if not v_rcand or \
               (v_lcand and in_circle(rcand.dest, rcand.org, lcand.org, lcand.dest) == 1):
                # Add cross edge rbase from rcand.dest to rbase.dest.
                rbase = connect(lcand, rbase.sym)
            else:
                # Add cross edge rbase from rbase.org to lcand.dest
                rbase = connect(rbase.sym, rcand.sym)

        return ldo, rdo


# -----------------------------------------------------------------
# Predicates


def in_circle(a, b, c, d):
    """Does d lie inside of circumcircle abc?"""
    adx, ady = a[0]-d[0], a[1]-d[1]
    bdx, bdy = b[0]-d[0], b[1]-d[1]
    cdx, cdy = c[0]-d[0], c[1]-d[1]
    det = np.linalg.det(
        ((adx, ady, adx**2 + ady**2),
         (bdx, bdy, bdx**2 + bdy**2),
         (cdx, cdy, cdx**2 + cdy**2)))
    return det < 0


def right_of(p, e):
    """Does point p lie to the right of the line of edge e?"""
    a, b = e.org, e.dest
    det = (a[0]-p[0]) * (b[1]-p[1]) - (a[1]-p[1]) * (b[0]-p[0])
    return det > 0


def left_of(p, e):
    """Does point p lie to the left of the line of edge e?"""
    a, b = e.org, e.dest
    det = (a[0]-p[0]) * (b[1]-p[1]) - (a[1]-p[1]) * (b[0]-p[0])
    return det < 0


# -----------------------------------------------------------------
# Topological operators


def make_edge(org, dest):
    """Creates a new edge. Assumes org and dest are points."""

    if p_coinside(org, dest):
        print("Can't create zero length edge: {}, {}.".format(org, dest))
        return None

    if e_exists(org, dest):
        print("Edge already exists: {}, {}.".format(org, dest))
        return None

    global edges
    e  = Edge(org, dest)
    es = Edge(dest, org)
    e.sym, es.sym = es, e  # make edges mutually symmetrical
    e.onext, e.oprev, e.dnext, e.dprev = e, e, e, e
    es.onext, es.oprev, es.dnext, es.dprev = es, es, es, es
    edges.append(e)
    return e


def splice(a, b):
    """Combines distinct edge rings / breaks the same ring in two pieces. If the ring is broken,
    the tearing will go between a and a.onext through a.org to between b and b.onext. It's not
    a purely topological splice. It takes into account position of edges on the plane and avoids
    creating 'folds' (when e.Onext appears CW of e, instead of CCW)."""

    if a == b:
        print("Splicing edge with itself, ignored: {}.".format(a))
        return

    if not p_coinside(a.org, b.org):
        print("Can't splice edges with distinct origins: {}, {}.".format(a, b))
        return

    # IF a and b are not in the same ring -- choose the appropriate edges and check for folds
    if not e_same_ring(a, b):
        a = e_first_cw(b, a)
        b = e_first_cw(a, b)
        if (e_cw_angle(a, b.onext) < e_cw_angle(a, b)) or \
           (e_cw_angle(b, a.onext) < e_cw_angle(b, a)):
            print("Can't splice edges with overlapping rings: {}, {}.".format(a, b))
            return

    # splice
    a.onext.set_oprev(b)
    b.onext.set_oprev(a)
    tmp = a.onext
    a.set_onext(b.onext)
    b.set_onext(tmp)


def connect(a, b):
    """Adds a new edge e connecting the destination of a to the origin of b, in such a way that
    a Left = e Left = b Left after the connection is complete."""
    e = make_edge(a.dest, b.org)
    if e is None:
        return None
    splice(e, a.dprev.sym)
    splice(e.sym, b)
    return e


def delete_edge(e):
    """Disconnects the edge e from the rest of the structure (this may cause the rest of the
    structure to fall apart in two separate components)."""
    splice(e, e.oprev)
    splice(e.sym, e.sym.oprev)
    global edges
    if e in edges:
        edges.remove(e)
    if e.sym in edges:
        edges.remove(e.sym)


def swap(e):
    """Given an edge e whose left and right faces are triangles, detaches e and connects it
    to the other two vertices of the quadrilateral thus formed."""
    a, b = e.oprev, e.sym.oprev
    splice(e, a); splice(e.sym, b)         # detach
    e.set_org(a.dest); e.set_dest(b.dest)  # reposition
    splice(e, a.sym.oprev); splice(e.sym, b.sym.oprev)  # attach


# -----------------------------------------------------------------
# Auxiliary methods


def p_sort(points):
    """Returns a copy of points sorted by x coordinate, y is a tiebreaker."""
    p = points.copy()
    p.view(dtype=[('f0', p.dtype), ('f1', p.dtype)]).sort(order=['f0', 'f1'], axis=0)
    return p


def p_remdup(points):
    """Remove duplicates."""
    if len(points) < 2:
        return points
    dupes = [i for i in range(1, len(points)) if p_coinside(points[i], points[i-1])]
    if dupes:
        return np.delete(points, dupes, 0)
    return points


def p_coinside(p1, p2):
    """Returns True if p1 has the same coordinates as p2, False otherwise."""
    return p1[0] == p2[0] and p1[1] == p2[1]


def e_exists(org, dest):
    """Returns True if there already exists an edge with given endpoints (any order)."""
    for e in edges:
        if (p_coinside(e.org, org) and p_coinside(e.dest, dest)) or \
           (p_coinside(e.org, dest) and p_coinside(e.dest, org)):
            return True
    return False


def e_same_ring(a, b):
    """Returns True if edges a and b are in the same ring, False otherwise."""
    e = a.onext
    while e != a:
        if e == b:
            return True
        e = e.onext
    return False


def e_first_cw(a, b):
    """Searches ring of b for the first CW edge with respect to a."""
    e = b
    e_cand = b
    CW_ang = e_cw_angle(a, b)
    while e.onext != b:
        ang = e_cw_angle(a, e.onext)
        if  ang < CW_ang:
            e_cand = e.onext
            CW_ang = ang
        e = e.onext
    return e_cand


def e_cw_angle(a, b):
    return cw_angle(e_angle(a), e_angle(b))


def e_angle(e):
    return angle_to(e.org, e.dest)


def angle_to(p0, p1):
    """Assumes p0 and p1 are points. Returns angle p0 -> p1 in radians."""
    return math.atan2(p1[1] - p0[1], p1[0] - p0[0])


def cw_angle(a0, a1):
    """Assumes a0, a1 are angles. Returns CW angle a0 -> a1."""
    if a0 == a1:
        return 0
    if a0 < a1:
        return a1 - a0
    return math.pi*2 + a1 - a0


def ccw_angle(a0, a1):
    """Assumes a0, a1 are angles. Returns positive CCW angle a0 -> a1."""
    if a0 == a1: return 0
    if a1 < a0: return a0 - a1
    return math.pi*2 + a0 - a1
