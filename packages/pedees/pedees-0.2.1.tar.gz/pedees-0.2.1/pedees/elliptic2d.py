#!/usr/bin/env python

import numpy
import math

class Elliptic2d:

	def __init__(self, fFunc, gFunc, sFunc):
		"""
		Constructor
		@param fFunc f in -div(f grad phi) + g phi = s
		@param gFunc g in -div(f grad phi) + g phi = s
		@param sFunc s source function
		"""

		self.fFunc = fFunc
		self.gFunc = gFunc
		self.sFunc = sFunc

		self.mat = {}
		self.sourceVec = []

		self.triangulation = None

	def assemble(self, tri):
		"""
		Assemble the stiffness matrix and the source vector
		@param tri triangulation 
		"""

		self.triangulation = tri
		n = len(tri.points)
		self.sourceVec = numpy.zeros( (n,), numpy.float64 )

		for i, iabc in tri.triangles.items():

			ia, ib, ic = iabc
			pa, pb, pc = tri.points[ia], tri.points[ib], tri.points[ic]

			# centroid 
			pMid = (pa + pb + pc)/3.0
			fxx = fyy = self.fFunc(pMid)

			ga = self.gFunc(pa)
			gb = self.gFunc(pb)
			gc = self.gFunc(pc)

			sa = self.sFunc(pa)
			sb = self.sFunc(pb)
			sc = self.sFunc(pc)

			xcb = pc[0] - pb[0]
			ycb = pc[1] - pb[1]
			xac = pa[0] - pc[0]
			yac = pa[1] - pc[1]
			xba = pb[0] - pa[0]
			yba = pb[1] - pa[1]

			area = -xba*yac + yba*xac
			if area < 0:
				print '*** area = ', area, ' for ia, ib, ic = ', ia, ib, ic

			fOverA = 0.25*(fxx + fyy)/area

			faa = fOverA * (ycb*ycb + xcb*xcb) \
			      + (ga/ 20. + gb/ 60. + gc/ 60.)*area

			fab = fOverA * (ycb*yac + xcb*xac) \
			      + (ga/ 60. + gb/ 60. + gc/120.)*area

			fac = fOverA * (ycb*yba + xcb*xba) \
			      + (ga/ 60. + gb/120. + gc/ 60.)*area

			fbb = fOverA * (yac*yac + xac*xac) \
			      + (ga/ 60. + gb/ 20. + gc/ 60.)*area

			fbc = fOverA * (yac*yba + xac*xba) \
			      + (ga/120. + gb/ 60. + gc/ 60.)*area

			fcc = fOverA * (yba*yba + xba*xba) \
			      + (ga/ 60. + gb/ 60. + gc/ 20.)*area

			self.mat[ia, ia] = self.mat.get((ia, ia), 0.0) + faa
			self.mat[ia, ib] = self.mat.get((ia, ib), 0.0) + fab
			self.mat[ia, ic] = self.mat.get((ia, ic), 0.0) + fac
			self.mat[ib, ib] = self.mat.get((ib, ib), 0.0) + fbb
			self.mat[ib, ic] = self.mat.get((ib, ic), 0.0) + fbc
			self.mat[ic, ic] = self.mat.get((ic, ic), 0.0) + fcc

			# make sure matrix is Hermitian
			self.mat[ib, ia] = self.mat[ia, ib]
			self.mat[ic, ia] = self.mat[ia, ic]
			self.mat[ic, ib] = self.mat[ib, ic]

			self.sourceVec[ia] += area*(sa/12.0 + sb/24.0 + sc/24.0)
			self.sourceVec[ib] += area*(sa/24.0 + sb/12.0 + sc/24.0)
			self.sourceVec[ic] += area*(sa/24.0 + sb/24.0 + sc/12.0)

	def applyBoundaryConditions(self, edge2Vals):
		"""
		f d phi/dn + b*phi = c
		Default boundary conditions are zero-Neumann
		@param edge2Vals dictionary of edge to (b, c) values
		"""
		for edge, vals in edge2Vals.items():

			i1, i2 = edge

			# distance between nodes
			d = self.triangulation.points[i2] - self.triangulation.points[i1]
			deltaLength = math.sqrt( numpy.dot(d, d) )

			# modification of the stiffness matrix
			diag = deltaLength * vals[0] / 3.0
			offDiag = deltaLength * vals[0] / 6.0
			self.mat[i1, i1] += diag
			self.mat[i2, i2] += diag
			self.mat[i1, i2] = self.mat.get((i1, i2), 0.0) + offDiag
			self.mat[i2, i1] = self.mat.get((i2, i1), 0.0) + offDiag

			# modification of the source term
			sVal = deltaLength * vals[1] / 2.0
			self.sourceVec[i1] += sVal
			self.sourceVec[i2] += sVal

	def getStiffnessMatrix(self):
		return self.mat

	def getSourceVector(self):
		return self.sourceVec