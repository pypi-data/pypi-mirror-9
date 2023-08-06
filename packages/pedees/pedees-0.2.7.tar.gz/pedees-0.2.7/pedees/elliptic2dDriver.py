#/usr/bin/env python

from delaunay2d import Delaunay2d
from elliptic2dDriverBase import Elliptic2dDriverBase
import numpy
from math import pi, cos, sin, tan, acos, asin, atan2, exp, log, sqrt

class Elliptic2dDriver(Elliptic2dDriverBase):

  def triangulate(self, xfunc, yfunc, numCells=1000):

    # number of boundary points
    nt = 2*int(sqrt(numCells))
    dt = 1.0/float(nt)

    # compute the boundary points
    xmins =  float('inf') * numpy.ones( (2,), numpy.float64 )
    xmaxs = -float('inf') * numpy.ones( (2,), numpy.float64 )
    for i in range(nt):
      t = i * dt
      x, y = eval(xfunc), eval(yfunc)
      xmins[0] = min(xmins[0], x)
      xmins[1] = min(xmins[1], y)
      xmaxs[0] = max(xmaxs[0], x)
      xmaxs[1] = max(xmaxs[1], y)
      self.boundaryPoints.append( numpy.array([x, y]) )

    # rough estimate of the max triangle area
    maxArea = (xmaxs[0] - xmins[0])*(xmaxs[1] - xmins[1])/float(numCells)
    self.delny = Delaunay2d(self.boundaryPoints, maxArea=maxArea)
    self.delny.triangulate()
    self.delny.makeDelaunay()
    self.delny.refine()
    self.delny.makeDelaunay() # this may not be necessary
      
################################################################################
def main():

  e = Elliptic2dDriver(fFunc='1.0', gFunc='0.0', sFunc='0.0')
  
  e.triangulate(xfunc='cos(2*pi*t)', yfunc='sin(2*pi*t)', numCells = 100)
  e.assemble()

  e.applyBoundaryConditions(bFunc='1.0', cFunc='sin(2*pi*x) + 3')

  e.solve()

  try:
    # requires Tkinter
    e.show()
  except:
    pass

if __name__ == '__main__':
  main()
