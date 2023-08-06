#/usr/bin/env python

from delaunay2d import Delaunay2d
from elliptic2dDriverBase import Elliptic2dDriverBase
import numpy
import math

class Elliptic2dDriverDiscretePoints(Elliptic2dDriverBase):

  def triangulate(self, boundaryPoints, numCells=1000):
      
    self.boundaryPoints = [ numpy.array(p, numpy.float64) for p in boundaryPoints ]

    # compute the box dimensions
    xmins =  float('inf') * numpy.ones( (2,), numpy.float64 )
    xmaxs = -float('inf') * numpy.ones( (2,), numpy.float64 )
    for p in self.boundaryPoints:
      x, y = p[0], p[1]
      xmins[0] = min(xmins[0], x)
      xmins[1] = min(xmins[1], y)
      xmaxs[0] = max(xmaxs[0], x)
      xmaxs[1] = max(xmaxs[1], y)

    # add Steiner points. Do a triangulation without the Delaunay step. 
    # Iterate over the boundary edges and add points if edge length 
    # is > maxEdgeLength
    tri = Delaunay2d(self.boundaryPoints, maxArea=float('inf')) # no refinement
    tri.triangulate() # basic triangulation
    xmins, xmaxs = tri.getBoxLimits()

    # rough estimate of the max triangle area
    maxArea = (xmaxs[0] - xmins[0])*(xmaxs[1] - xmins[1])/float(numCells)
    
    maxEdgeLength = math.sqrt(maxArea) * 2.0/0.707
      
    for boundaryEdge in tri.getBoundaryEdges():
      ia, ib = boundaryEdge
      du = self.boundaryPoints[ib] - self.boundaryPoints[ia]
      distance = math.sqrt( numpy.dot(du, du) )
      numSteinerPoints = int(distance // maxEdgeLength)
      du /= float(numSteinerPoints + 1)
      # add the Steiner points
      for i in range(1, numSteinerPoints):
        pt = self.boundaryPoints[ia] + i*du
        self.boundaryPoints.append(pt)

    self.delny = Delaunay2d(self.boundaryPoints, maxArea=maxArea)
    self.delny.triangulate()
    self.delny.makeDelaunay()
    self.delny.refine()
    self.delny.makeDelaunay() # this may not be necessary
      
################################################################################
def test1():

  points = [ [0., 0.], [0., 1.], [1., 1.] ]
  e = Elliptic2dDriverDiscretePoints(fFunc='1.0', gFunc='0.0', sFunc='0.0')
  e.triangulate(boundaryPoints=points, numCells = 100)
  e.assemble()

  e.applyBoundaryConditions(bFunc='1.0', cFunc='sin(2*pi*x) + 3.0')

  e.solve()

  try:
    # requires Tkinter
    e.show()
  except:
    pass

def test2():

  elliptic = Elliptic2dDriverDiscretePoints(fFunc='1.0', gFunc='0.0', sFunc='0.0')

  bpoints = [numpy.array([0, 0]), numpy.array([0, 1]), numpy.array([1, 1])]
  elliptic.triangulate(boundaryPoints = bpoints, numCells = 100)
  elliptic.assemble()

  elliptic.applyBoundaryConditions(bFunc='1.0', cFunc='2.0')

  diag = elliptic.solve()

  try:
    # requires Tkinter
    elliptic.show()
  except:
    pass

if __name__ == '__main__':
  test1()
  test2()
