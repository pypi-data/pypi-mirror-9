#/usr/bin/env python

from delaunay2d import Delaunay2d
from inside import Inside
from elliptic2d import Elliptic2d
from cg import Cg
import math
import numpy
from math import pi, cos, sin, tan, acos, asin, atan2, exp, log

class Elliptic2dDriver:

  def __init__(self, fFunc, gFunc, sFunc, xFunc, yFunc):
    self.fFuncStr = fFunc
    self.gFuncStr = gFunc
    self.sFuncStr = sFunc
    self.xFuncStr = xFunc
    self.yFuncStr = yFunc

    self.delny = None
    self.ellipt = Elliptic2d(self.ffunc, self.gfunc, self.sfunc)
    self.slvr = None
    self.solution = None
  
  def getTriangulation(self):
    return self.delny

  def getSolution(self):
    return self.solution

  def triangulate(self, numCells=1000):

    # number of boundary points
    self.nt = 2*int(math.sqrt(numCells))
    self.dt = 1.0/float(self.nt)

    # compute the boundary points
    points = []
    xmins =  float('inf') * numpy.ones( (2,), numpy.float64 )
    xmaxs = -float('inf') * numpy.ones( (2,), numpy.float64 )
    for i in range(self.nt):
      t = i * self.dt
      x, y = self.xfunc(t), self.yfunc(t)
      xmins[0] = min(xmins[0], x)
      xmins[1] = min(xmins[1], y)
      xmaxs[0] = max(xmaxs[0], x)
      xmaxs[1] = max(xmaxs[1], y)
      points.append( numpy.array([x, y]) )

    # rough estimate of the max triangle area
    maxArea = (xmaxs[0] - xmins[0])*(xmaxs[1] - xmins[1])/float(numCells)
    self.delny = Delaunay2d(points, maxArea=maxArea)
    self.delny.triangulate()
    self.delny.makeDelaunay()
    self.delny.refine()
    self.delny.makeDelaunay() # this may not be necessary

    self.ellipt.assemble(self.delny)

  def ffunc(self, xy):
    x, y = xy
    return eval(self.fFuncStr)

  def gfunc(self, xy):
    x, y = xy
    return eval(self.gFuncStr)

  def sfunc(self, xy):
    x, y = xy
    return eval(self.sFuncStr)

  def xfunc(self, t):
  	return eval(self.xFuncStr)

  def yfunc(self, t):
  	return eval(self.yFuncStr)

  def applyBoundaryConditions(self, bFunc, cFunc):

    bcs = {}
    for i in range(self.nt):
      t = (i + 0.5) * self.dt
      b, c = eval(bFunc), eval(cFunc)
      bcs[i, (i+1)%self.nt] = (b, c)

    self.ellipt.applyBoundaryConditions(bcs)

    self.slvr = Cg(self.ellipt.getStiffnessMatrix(), \
                              self.ellipt.getSourceVector())

  def solve(self):
        
    # initial guess
    self.n = len(self.delny.points)

    mat = self.ellipt.getStiffnessMatrix()

    # use diagonal matrix as preconditioner
    precond = numpy.array( [mat[i, i] for i in range(self.n)] )

    # initial guess
    x0 = numpy.zeros( (self.n,), numpy.float64 )

    # max number of iterations
    numIters = self.n

    self.solution = self.slvr.solve(precond = precond, x0 = x0, 
                           numIters=numIters, tol=1.e-10, verbose=True)


  def show(self):
		from plot import Plot
		pl = Plot(self.delny, width=500, height=500)
		pl.show(self.solution)
    
      
################################################################################
def main():

  e = Elliptic2dDriver(fFunc='1.0', gFunc='0.0', sFunc='0.0', xFunc='cos(2*pi*t)', yFunc='sin(2*pi*t)')
  e.triangulate(numCells = 100)

  e.applyBoundaryConditions(bFunc='1.0', cFunc='sin(2*pi*t)')

  e.solve()

  e.show()

if __name__ == '__main__':
  main()
