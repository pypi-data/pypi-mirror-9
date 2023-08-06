#/usr/bin/env python

from delaunay2d import Delaunay2d
from inside import Inside
from elliptic2d import Elliptic2d
from cg import Cg
import math
import numpy
from math import pi, cos, sin, tan, acos, asin, atan2, exp, log

class Elliptic2dDriverBase:

  def __init__(self, fFunc, gFunc, sFunc):
    self.fFuncStr = fFunc
    self.gFuncStr = gFunc
    self.sFuncStr = sFunc

    self.boundaryPoints = []
    self.delny = None
    self.ellipt = Elliptic2d(self.ffunc, self.gfunc, self.sfunc)
    self.slvr = None
    self.solution = None
  
  def getTriangulation(self):
    return self.delny

  def getSolution(self):
    return self.solution

  def assemble(self):
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

  def applyBoundaryConditions(self, bFunc, cFunc):

    bcs = {}
    nt = len(self.boundaryPoints)
    for i0 in range(nt):
      x0, y0 = self.boundaryPoints[i0]
      i1 = (i0 + 1) % nt
      x1, y1 = self.boundaryPoints[i1]
      x, y = 0.5*(x0 + x1), 0.5*(y0 + y1)
      b, c = eval(bFunc), eval(cFunc)
      bcs[i0, i1] = (b, c)

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

    diag = {}
    self.solution = self.slvr.solve(precond = precond, x0 = x0, 
                           numIters=numIters, tol=1.e-10, verbose=True, diag=diag)
    return diag

  def show(self):
		from plot import Plot
		pl = Plot(self.delny, width=500, height=500)
		pl.show(self.solution)
