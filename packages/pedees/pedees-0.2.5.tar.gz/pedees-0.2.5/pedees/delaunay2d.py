#!/usr/bin/env python

import numpy
import math
import copy
import operator

from inside import Inside

class Delaunay2d:

  # small number to define what we mean by positive
  EPS = 1.23456789e-14

  def __init__(self, points, maxArea):
    """
    Constructor
    @param points initial set of points
    @param maxArea maximum cell area, will refine cells to satisfy this criterion
    """

    # data structures
    self.points = points[:] # copy

    # compute low/high corner points of domain
    n = len(points[0]) # must have at least one point
    self.xmins = +float('inf') * numpy.ones( (n,), numpy.float64 )
    self.xmaxs = -float('inf') * numpy.ones( (n,), numpy.float64 )
    for i in range(n):
      for p in points:
        self.xmins[i] = min(self.xmins[i], p[i])
        self.xmaxs[i] = max(self.xmaxs[i], p[i])

    # id -> [point indices], a dict so we can easily remove elements
    # without breaking the indexing
    self.triangles = {} 
    # counter keeps track of the highest triangle ID number
    self.triangleCounter = 0

    self.edge2Triangles = {} # edge to triangle(s) map
    self.boundaryEdges = set()
    self.maxArea = maxArea

    # keep track of the triangles to remove
    self.trianglesToRemove = set()

  def getPoints(self):
    """
    @return points
    """
    return self.points

  def getTriangles(self):
    """
    @return triangles
    """
    return self.triangles.values()

  def getEdges(self):
    """
    @return egdes
    """
    return self.edge2Triangles.keys()

  def getBoundaryEdges(self):
    """
    @return boundary edges
    """
    return self.boundaryEdges

  def carve(self, xyPoints):
    """
    Remove cells that are inside holes
    @param internalBoundaries list of closed contours
    """

    n = len(xyPoints)
    contour = [(i, i+1) for i in range(n - 1)] + [(n-1, 0)]

    # compute the center of gravity location for each triangle. If the 
    # point is inside the contour then tag the triangle for removal.
    trianglesToRemove = set()

    # iterate over all the cells
    for tId, tVals in self.triangles.items():

      # compute the center of gravity of the cell
      n = len(tVals)
      cgPosition = reduce(operator.add, [self.points[i] for i in tVals])/float(n)

      # is the center of gravity inside the contour?
      insideChecker = Inside(xyPoints, contour, self.xmins, self.xmaxs)
      if insideChecker.isInside(cgPosition):
        # tag cell for removal
        trianglesToRemove.add(tId)

    # now remove
    self.removeCells(trianglesToRemove)

  def triangulate(self):
    """
    Triangulate the domain
    """

    # compute center of gravity
    cg = numpy.zeros((2,), numpy.float64)
    for pt in self.points:
      cg += pt
    cg /= len(self.points)

    # sort
    def distanceSquare(pt):
      d = pt - cg
      return numpy.dot(d, d)
    self.points.sort(key = distanceSquare)

    # create first triangle, make sure we're getting a non-zero area otherwise
    # drop the points
    area = 0.0
    index = 0
    stop = False
    while not stop and index + 2 < len(self.points):
      area = self.getArea(index, index + 1, index + 2)
      if abs(area) < self.EPS:
        del self.points[index]
      else:
        stop = True
    if index <= len(self.points) - 3:
      tri = [index, index + 1, index + 2]
      self.makeCounterClockwise(tri)
      self.triangles[self.triangleCounter] = tri
      self.triangleCounter += 1

      # boundary edges
      e01 = (tri[0], tri[1])
      self.boundaryEdges.add(e01)
      e12 = (tri[1], tri[2])
      self.boundaryEdges.add(e12)
      e20 = (tri[2], tri[0])
      self.boundaryEdges.add(e20)

      e01 = self.makeKey(e01[0], e01[1])
      self.edge2Triangles[e01] = [0,]

      e12 = self.makeKey(e12[0], e12[1])
      self.edge2Triangles[e12] = [0,]

      e20 = self.makeKey(e20[0], e20[1])
      self.edge2Triangles[e20] = [0,]

    else:
      # all the points fall on a line
      return

    # add additional points
    for i in range(3, len(self.points)):
      self.addPoint(i)

    #self.refine()

  def makeDelaunay(self):

    flipped = True
    while flipped:
      flipped = self.flipEdges()    

  def refine(self):

    stop = False
    while not stop:

      tIndices = []
      for i, tri in self.triangles.items():
        ia, ib, ic = tri
        area = 0.5 * self.getArea(ia, ib, ic)
        if area > self.maxArea:
          tIndices.append(i)
          
      stop = (len(tIndices) == 0)

      for ti in tIndices:
        self.refineCell(ti)

      # remove triangles
      for ti in self.trianglesToRemove:
        del self.triangles[ti]
      self.trianglesToRemove = set()

      self.makeDelaunay()


  def refineCell(self, index):
    """
    Add middle point to cell
    @param index triangle ID

    @note will append "index" to self.trianglesToRemove. This method does not 
    remove the triangle but only keep track of the triangles to remove. The 
    self.edge2Triangles dict will be updated. 
    """
    ia, ib, ic = self.triangles[index]

    newPoint = (self.points[ia] + self.points[ib] + self.points[ic])/3.0
    newPointIndex = len(self.points)

    # new set of edges
    ean = (ia, newPointIndex)
    ebn = (ib, newPointIndex)
    ecn = (ic, newPointIndex)

    # add the point to our list
    self.points.append(newPoint)

    # add new cells
    tabn = self.triangleCounter
    tbcn = tabn + 1
    tcan = tbcn + 1
    self.triangleCounter += 3
    self.triangles[tabn] = (ia, ib, newPointIndex)
    self.triangles[tbcn] = (ib, ic, newPointIndex)
    self.triangles[tcan] = (ic, ia, newPointIndex)

    # old edges
    eab = self.makeKey(ia, ib)
    ebc = self.makeKey(ib, ic)
    eca = self.makeKey(ic, ia)
    # neighbors to these edges
    tabNeigh = self.edge2Triangles[eab]
    tbcNeigh = self.edge2Triangles[ebc]
    tcaNeigh = self.edge2Triangles[eca]
    # replace old index with the new triangle index
    self.edge2Triangles[eab] = [i if i != index else tabn for i in tabNeigh]
    self.edge2Triangles[ebc] = [i if i != index else tbcn for i in tbcNeigh]
    self.edge2Triangles[eca] = [i if i != index else tcan for i in tcaNeigh]
    # add the new edges
    self.edge2Triangles[ean] = [tabn, tcan]
    self.edge2Triangles[ebn] = [tbcn, tabn]
    self.edge2Triangles[ecn] = [tcan, tbcn]

    self.trianglesToRemove.add(index)

  def removeCells(self, indices):
    """
    Remove triangles
    @param indices triangle IDs to remove
    """
    for index in indices:
      del self.triangles[index]
      # remove any reference to triangle index in self.edge2Triangles
      for e, t in self.edge2Triangles.items():
        if t.count(index) > 0:
          i = t.index(index)
          del self.edge2Triangles[e][i]
          if len(self.edge2Triangles[e]) == 0:
            # remove the edge since there is triangle attached to it
            del self.edge2Triangles[e]

  def getArea(self, ip0, ip1, ip2):
    """
    Compute the parallelipiped area
    @param ip0 index of first vertex
    @param ip1 index of second vertex
    @param ip2 index of third vertex
    """
    d1 = self.points[ip1] - self.points[ip0]
    d2 = self.points[ip2] - self.points[ip0]
    return (d1[0]*d2[1] - d1[1]*d2[0])

  def isEdgeVisible(self, ip, edge):
    """
    Return true iff the point lies to its right when the edge points down
    @param ip point index
    @param edge (2 point indices with orientation)
    @return True if visible    
    """
    area = self.getArea(ip, edge[0], edge[1])
    if area < -self.EPS:
      return True
    return False

  def makeCounterClockwise(self, ips):
    """
    Re-order nodes to ensure positive area (in-place operation)
    """
    area = self.getArea(ips[0], ips[1], ips[2])
    if area < -self.EPS:
      ip1, ip2 = ips[1], ips[2]
      # swap
      ips[1], ips[2] = ip2, ip1

  def flipOneEdge(self, edge):
    """
    Flip one edge then update the data structures
    @return set of edges to interate over at next iteration
    """

    # start with empty set
    res = set()

    # assume edge is sorted
    tris = self.edge2Triangles.get(edge, [])
    if len(tris) < 2:
        # nothing to do, just return
        return res

    iTri1, iTri2 = tris
    tri1 = self.triangles.get(iTri1, -1)
    tri2 = self.triangles.get(iTri2, -1)
    if tri1 < 0 or tri2 < 0:
      # triangle has been removed
      return res

    # find the opposite vertices, not part of the edge
    iOpposite1 = -1
    iOpposite2 = -1
    for i in range(3):
      if not tri1[i] in edge:
        iOpposite1 = tri1[i]
      if not tri2[i] in edge:
        iOpposite2 = tri2[i]

    # compute the 2 angles at the opposite vertices
    da1 = self.points[edge[0]] - self.points[iOpposite1]
    db1 = self.points[edge[1]] - self.points[iOpposite1]
    da2 = self.points[edge[0]] - self.points[iOpposite2]
    db2 = self.points[edge[1]] - self.points[iOpposite2]
    crossProd1 = self.getArea(iOpposite1, edge[0], edge[1])
    crossProd2 = self.getArea(iOpposite2, edge[1], edge[0])
    dotProd1 = numpy.dot(da1, db1)
    dotProd2 = numpy.dot(da2, db2)
    angle1 = abs(math.atan2(crossProd1, dotProd1))
    angle2 = abs(math.atan2(crossProd2, dotProd2))
    
    # Delaunay's test
    if angle1 + angle2 > math.pi*(1.0 + self.EPS):

      # flip the triangles
      #             / ^ \                    / b \
      # iOpposite1 + a|b + iOpposite2  =>   + - > +
      #             \   /                    \ a /

      newTri1 = [iOpposite1, edge[0], iOpposite2] # triangle a
      newTri2 = [iOpposite1, iOpposite2, edge[1]] # triangle b
      self.makeCounterClockwise(newTri1)
      self.makeCounterClockwise(newTri2)

      # update the triangle data structure
      self.triangles[iTri1] = newTri1
      self.triangles[iTri2] = newTri2

      # now handle the topolgy of the edges

      # remove this edge
      del self.edge2Triangles[edge]

      # add new edge
      e = self.makeKey(iOpposite1, iOpposite2)
      self.edge2Triangles[e] = [iTri1, iTri2]

      # modify two edge entries which now connect to 
      # a different triangle
      e = self.makeKey(iOpposite1, edge[1])
      v = self.edge2Triangles[e]
      for i in range(len(v)):
        if v[i] == iTri1:
          v[i] = iTri2
      res.add(e)

      e = self.makeKey(iOpposite2, edge[0])
      v = self.edge2Triangles[e]
      for i in range(len(v)):
        if v[i] == iTri2:
          v[i] = iTri1
      res.add(e)

      # these two edges might need to be flipped at the
      # next iteration
      res.add(self.makeKey(iOpposite1, edge[0]))
      res.add(self.makeKey(iOpposite2, edge[1]))

    return res 

  def flipEdges(self):
    """
    Flip edges to statisfy Delaunay's criterion
    """

    # start with all the edges
    edgeSet = set(self.edge2Triangles.keys())

    continueFlipping = True

    while continueFlipping:

      #
      # iterate until there are no more edges to flip
      #

      # collect the edges to flip
      newEdgeSet = set()
      for edge in edgeSet:
        # union
        newEdgeSet |= self.flipOneEdge(edge)

      edgeSet = copy.copy(newEdgeSet)
      continueFlipping = (len(edgeSet) > 0)

  def addPoint(self, ip):
    """
    Add point
    @param ip point index
    """

    # collection for later updates
    boundaryEdgesToRemove = set()
    boundaryEdgesToAdd = set()

    for edge in self.boundaryEdges:

      if self.isEdgeVisible(ip, edge):

        # create new triangle
        newTri = [edge[0], ip, edge[1]]
        self.triangles[self.triangleCounter] = newTri
        self.triangleCounter += 1

        # update the edge to triangle map
        e = list(edge[:])
        e.sort()
        iTri = self.triangleCounter - 1 
        self.edge2Triangles[tuple(e)].append(iTri)

        # add the two boundary edges
        e1 = [ip, edge[0]]
        e1.sort()
        e1 = tuple(e1)
        e2 = [edge[1], ip]
        e2.sort()
        e2 = tuple(e2)
        v1 = self.edge2Triangles.get(e1, [])
        v1.append(iTri)
        v2 = self.edge2Triangles.get(e2, [])
        v2.append(iTri)
        self.edge2Triangles[e1] = v1
        self.edge2Triangles[e2] = v2

        # keep track of the boundary edges to update
        boundaryEdgesToRemove.add(edge)
        boundaryEdgesToAdd.add( (edge[0], ip) )
        boundaryEdgesToAdd.add( (ip, edge[1]) )

    # update the boundary edges
    for bedge in boundaryEdgesToRemove:
      self.boundaryEdges.remove(bedge)
    for bedge in boundaryEdgesToAdd:
      bEdgeSorted = list(bedge)
      bEdgeSorted.sort()
      bEdgeSorted = tuple(bEdgeSorted)
      if len(self.edge2Triangles[bEdgeSorted]) == 1:
        # only add boundary edge if it does not appear
        # twice in different order
        self.boundaryEdges.add(bedge)

    # recursively flip edges
    #flipped = True
    #while flipped:
      #flipped = self.flipEdges()

  def makeKey(self, i1, i2):
    """
    Make a tuple key such at i1 < i2
    """
    if i1 < i2:
      return (i1, i2)
    return (i2, i1)

  def show(self, width=500, height=500, showVertices=False, showCells=False, showContour=[]):

    import Tkinter

    xmin = min([p[0] for p in self.points])
    ymin = min([p[1] for p in self.points])
    xmax = max([p[0] for p in self.points])
    ymax = max([p[1] for p in self.points])
    padding = 5
    w = width - 2*padding
    h = height - 2*padding

    master = Tkinter.Tk()
    c = Tkinter.Canvas(master, width=width, height=height)
    c.pack()
    for e in self.edge2Triangles:
      i1, i2 = e
      xp1 = padding + int(w*(self.points[i1][0] - xmin)/(xmax - xmin))
      yp1 = padding + int(h*(ymax - self.points[i1][1])/(ymax - ymin))
      xp2 = padding + int(w*(self.points[i2][0] - xmin)/(xmax - xmin))
      yp2 = padding + int(h*(ymax - self.points[i2][1])/(ymax - ymin))
      c.create_line(xp1, yp1, xp2, yp2)

    if showVertices:
      for i in range(len(self.points)):
        xp = padding + int(w*(self.points[i][0] - xmin)/(xmax - xmin))
        yp = padding + int(h*(ymax - self.points[i][1])/(ymax - ymin))
        c.create_text(xp, yp, text=str(i))

    if showCells:
      for tId, tVals in self.triangles.items():
        cg = reduce(operator.add, [self.points[i] for i in tVals])/float(len(tVals))
        xp = padding + int(w*(cg[0] - xmin)/(xmax - xmin))
        yp = padding + int(h*(ymax - cg[1])/(ymax - ymin))
        c.create_text(xp, yp, text=str(tId))

    if len(showContour) > 0:
      for i in range(len(showContour) - 1):
        xp1 = padding + int(w*(showContour[i][0] - xmin)/(xmax - xmin))
        yp1 = padding + int(h*(ymax - showContour[i][1])/(ymax - ymin))
        xp2 = padding + int(w*(showContour[i+1][0] - xmin)/(xmax - xmin))
        yp2 = padding + int(h*(ymax - showContour[i+1][1])/(ymax - ymin))
        c.create_line(xp1, yp1, xp2, yp2, fill='red')


    Tkinter.mainloop()

#############################################################################

def testOneTriangle():
  xyPoints = [numpy.array([0., 0.]), numpy.array([1., 0.]), numpy.array([0., 1.])]
  delaunay = Delaunay2d(xyPoints, maxArea=10.0)
  delaunay.triangulate()
  delaunay.makeDelaunay()
  print 'triangles: ', delaunay.getTriangles()
  print 'edges: ', delaunay.getEdges()

def testOneTriangle2():
  # points go clockwise
  xyPoints = [numpy.array([0., 0.]), numpy.array([0., 1.]), numpy.array([1., 0.])]
  delaunay = Delaunay2d(xyPoints, maxArea=10.0)
  delaunay.triangulate()
  delaunay.makeDelaunay()
  print 'triangles: ', delaunay.getTriangles()
  print 'edges: ', delaunay.getEdges()

def testTwoTriangles():
  xyPoints = [numpy.array([0., 0.]), numpy.array([1., 0.]), numpy.array([0., 1.]), numpy.array([1., 1.])]
  delaunay = Delaunay2d(xyPoints, maxArea=10.0)
  delaunay.triangulate()
  delaunay.makeDelaunay()
  print 'triangles: ', delaunay.getTriangles()
  print 'edges: ', delaunay.getEdges()
  #delaunay.show()

def testRandomTriangles():
  import random
  random.seed(1234)
  xyPoints = [numpy.array([random.random(), random.random()]) for i in range(1000)]
  delaunay = Delaunay2d(xyPoints, maxArea=10.0)
  delaunay.triangulate()
  delaunay.makeDelaunay()

def testRandomTrianglesRefine():
  import random
  random.seed(1234)
  xyPoints = [numpy.array([random.random(), random.random()]) for i in range(10)]
  delaunay = Delaunay2d(xyPoints, maxArea=0.005)
  delaunay.triangulate()
  delaunay.makeDelaunay()
  try:
    delaunay.show()
  except:
    pass

def testAnnulus():
  import math
  ntOut = 16
  dtOut = 2*math.pi/float(ntOut)
  ntIn = 4
  dtIn = 2*math.pi/float(ntIn)
  # outer contour
  xyPoints = [numpy.array([math.cos(i*dtOut), math.sin(i*dtOut)]) for i in range(ntOut)]
  # inner contour
  xyPointsInterior = [ numpy.array( [0.5*math.cos(i*dtIn), 0.5*math.sin(i*dtIn)] ) \
                       for i in range(ntIn)]
  xyPoints += xyPointsInterior
  delaunay = Delaunay2d(xyPoints, maxArea=0.01)
  delaunay.triangulate()
  #delaunay.makeDelaunay()
  #delaunay.refine()
  delaunay.carve(xyPointsInterior)
  delaunay.makeDelaunay()
  delaunay.refine()
  #delaunay.makeDelaunay()
  # carve out interior
  delaunay.carve(xyPointsInterior)
  try:
    delaunay.show(showCells=False, 
      showContour=xyPointsInterior, 
      showVertices=False)
  except:
    pass

if __name__ == '__main__': 
  testOneTriangle()
  testOneTriangle2()
  testTwoTriangles()
  testRandomTriangles()
  testRandomTrianglesRefine()
  testAnnulus()



