#/usr/bin/env python

from delaunay2d import Delaunay2d
from elliptic2d import Elliptic2d
from elliptic2dDriverBase import Elliptic2dDriverBase
import numpy

class Elliptic2dDriverDiscretePoints(Elliptic2dDriverBase):

  def triangulate(self, boundaryPoints, numCells=1000):
      
    self.boundaryPoints = [ numpy.array(p) for p in boundaryPoints ]

    # compute the box dimensions
    xmins =  float('inf') * numpy.ones( (2,), numpy.float64 )
    xmaxs = -float('inf') * numpy.ones( (2,), numpy.float64 )
    for p in self.boundaryPoints:
      x, y = p[0], p[1]
      xmins[0] = min(xmins[0], x)
      xmins[1] = min(xmins[1], y)
      xmaxs[0] = max(xmaxs[0], x)
      xmaxs[1] = max(xmaxs[1], y)

    # rough estimate of the max triangle area
    maxArea = (xmaxs[0] - xmins[0])*(xmaxs[1] - xmins[1])/float(numCells)
    self.delny = Delaunay2d(self.boundaryPoints, maxArea=maxArea)
    self.delny.triangulate()
    self.delny.makeDelaunay()
    self.delny.refine()
    self.delny.makeDelaunay() # this may not be necessary
      
################################################################################
def main():

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

if __name__ == '__main__':
  main()
