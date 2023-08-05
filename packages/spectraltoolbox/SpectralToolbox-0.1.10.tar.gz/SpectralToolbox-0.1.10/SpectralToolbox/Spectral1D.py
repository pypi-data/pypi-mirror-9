# -*- coding: utf-8 -*-

#
# This file is part of SpectralToolbox.
#
# SpectralToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpectralToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with SpectralToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

"""
 Spectral 1D
=========================================

Created on Thu Mar 29 11:33:32 2012

@author: Daniele Bigoni (dabi@imm.dtu.dk)

Description
-----------

Implementation of Spectral Methods in 1 dimension.

Available polynomials:
    * :ref:`ref_jacobi` or ``Spectral1D.JACOBI``
    * Hermite Physicist or ``Spectral1D.HERMITEP``
    * Hermite Function or ``Spectral1D.HERMITEF``
    * Hermite Probabilistic or ``Spectral1D.HERMITEP_PROB``
    * Laguerre Polynomial or ``Spectral1D.LAGUERREP``
    * Laguerre Function or ``Spectral1D.LAGUERREF``
    * ORTHPOL package (generation of recursion coefficients using [4]_)  or ``Spectral1D.ORTHPOL``

Available quadrature rules (related to selected polynomials):
    * Gauss or ``Spectral1D.GAUSS``
    * Gauss-Lobatto or ``Spectral1D.GAUSSLOBATTO``
    * Gauss-Radau or ``Spectral1D.GAUSSRADAU``

Available quadrature rules (without polynomial selection):
    * Kronrod-Patterson on the real line or ``Spectral1D.KPN`` (function ``Spectral1D.kpn(n)``)
    * Kronrod-Patterson uniform or ``Spectral1D.KPU`` (function ``Spectral1D.kpu(n)``)
    * Clenshaw-Curtis or ``Spectral1D.CC`` (function ``Spectral1D.cc(n)``)
    * Fejer's or ``Spectral1D.FEJ`` (function ``Spectral1D.fej(n)``)

.. _ref_jacobi:

Jacobi Polynomials
^^^^^^^^^^^^^^^^^^

Jacobi polynomials are defined on the domain :math:`\\Omega=[-1,1]` by the recurrence relation

.. math:: 
    
    xP^{(\\alpha,\\beta)}_n(x) =    & \\frac{2(n+1)(n+\\alpha+\\beta+1)}{(2n+\\alpha+\\beta+1)(2n+\\alpha+\\beta+2)} P^{(\\alpha,\\beta)}_{n+1}(x) \\
                                    & + \\frac{\\beta^2 - \\alpha^2}{(2n+\\alpha+\\beta)(2n+\\alpha+\\beta+2)} P^{(\\alpha,\\beta)}_{n}(x) \\
                                    & + \\frac{2(n+\\alpha)(n+\\beta)}{(2n+\\alpha+\\beta)(2n+\\alpha+\\beta+1)} P^{(\\alpha,\\beta)}_{n-1}(x)

with weight function

.. math::
    
    w(x;\\alpha,\\beta) = \\frac{\\Gamma(\\alpha+\\beta+2)}{2^{\\alpha+\\beta+1}\\Gamma(\\alpha+1)\\Gamma(\\beta+1)}(1-x)^\\alpha (1+x)^\\beta

.. note::
    
    In probability theory, the Beta distribution is defined on :math:`\\Psi=[0,1]` and its the Probability Distribution Function is
    
    .. math::
        
        \\rho_B(x;\\alpha,\\beta) = \\frac{\\Gamma(\\alpha+\\beta)}{\\Gamma(\\alpha)\\Gamma(\\beta)} x^{\\alpha-1} (1-x)**(\\beta-1)
    
    The relation betwen :math:`w(x;\\alpha,\\beta)` and :math:`\\rho_B(x;\\alpha,\\beta)` for :math:`x \\in \\Psi` is
    
    .. math::
        
        \\rho_B(x;\\alpha,\\beta) = 2 * w(2*x-1;\\beta-1,\\alpha-1)
    
    For example:
    
    >>> from scipy import stats
    >>> plot(xp,stats.beta(3,5).pdf(xp))
    >>> plot(xp,2.*Bx(xx,4,2),'--')
    >>> plot(xp,stats.beta(3,8).pdf(xp))
    >>> plot(xp,2.*Bx(xx,7,2),'--')

References  
----------

.. [1] "Implemenenting Spectral Methods for Partial Differential Equations" by David A. Kopriva, Springer, 2009

.. [2] J. Shen and L.L. Wang, “Some recent advances on spectral methods for unbounded domains”. Communications in Computational Physics, vol. 5, no. 2–4, pp. 195–241, 2009

.. [3] W.H. Press, Numerical Recipes: "The Art of Scientific Computing". Cambridge University Press, 2007

.. [4] W. Gautschi, "Algorithm 726: ORTHPOL -- a package of routines for generating orthogonal polynomials and Gauss-type quadrature rules". ACM Trans. Math. Softw., vol. 20, issue 1, pp. 21-62, 1994

.. [5] Y.Shi-jun, "Gauss-Radau and Gauss-Lobatto formulae for the Jacobi weight and Gori-Micchelli weight functions". Journal of Zhejiang University Science, vol. 3, issue 4, pp. 455-460

Examples
--------

"""

import sys
import warnings
import numpy as np
from numpy import linalg as LA
from numpy import fft as FFT
import math

from scipy.special import gamma as gammaF
from scipy.misc import factorial
from scipy.misc import comb as SPcomb
from scipy import sparse as scsp

import SparseGrids as SG
try:
    import orthpol
    ORTHPOL_SUPPORT = True
except ImportError:
    ORTHPOL_SUPPORT = False
    warnings.warn("SpectralToolbox.Spectral1D: The orthpol pacakge is not installed on this machine. Functionalities associated with this package are disabled.", ImportWarning)

JACOBI = 'Jacobi'
HERMITEP = 'HermiteP'
HERMITEF = 'HermiteF'
HERMITEP_PROB = 'HermitePprob'
LAGUERREP = 'LaguerreP'
LAGUERREF = 'LaguerreF'
ORTHPOL = 'ORTHPOL'
AVAIL_POLY = [JACOBI, HERMITEP, HERMITEF, HERMITEP_PROB, LAGUERREP, LAGUERREF, ORTHPOL]

GAUSS = 'Gauss'
GAUSSRADAU = 'GaussRadau'
GAUSSLOBATTO = 'GaussLobatto'
GQU = 'Gauss Uniform'
GQN = 'Gauss Normal'
KPU = 'Kronrod-Patterson Uniform'
KPN = 'Kronrod-Patterson Normal'
CC  = 'Clenshaw-Curtis Uniform'
FEJ = 'Fejer Uniform'
AVAIL_QUADPOINTS = [GAUSS, GAUSSRADAU, GAUSSLOBATTO, GQU, GQN, KPU, KPN, CC, FEJ]

class Poly1D(object):
    poly = None
    params = None
    sdout = None

    def __init__(self,poly,params,sdout=sys.stderr):
        """
        Initialization of the Polynomial instance.
        
        Syntax:
            ``p = Poly1D(poly,params)``
        
        Input:
            * ``poly`` = The orthogonal polynomial type desired
            * ``params`` = The parameters needed by the selected polynomial
            * ``sdout`` = (optional,default=sys.stderr) output stream for logging
        
        Description:
            This method generates an instance of the Poly1D class, to be used in order to generate
            orthogonal basis of the polynomial type selected. Avaliable polynomial types can be
            selected using their string name or by predefined attributes
                * 'Jacobi' or ``Spectral1D.JACOBI``
                * 'HermiteP' or ``Spectral1D.HERMITEP``
                * 'HermiteF' or ``Spectral1D.HERMITEF``
                * 'HermitePprob' or ``Spectral1D.HERMITEP_PROB``
                * 'LaguerreP' or ``Spectral1D.LAGUERREP``
                * 'LaguerreF' or ``Spectral1D.LAGUERREF``
                * 'ORTHPOL' or ``Spectral1D.ORTHPOL``
            Additional parameters are required for some polynomials.
            
            +--------------+--------------+
            | Polynomial   | Parameters   |
            +==============+==============+
            | Jacobi       | (alpha,beta) |
            +--------------+--------------+
            | HermiteP     | None         |
            +--------------+--------------+
            | HermiteF     | None         |
            +--------------+--------------+
            | HermitePprob | None         |
            +--------------+--------------+
            | LaguerreP    | alpha        |
            +--------------+--------------+
            | LaguerreF    | alpha        |
            +--------------+--------------+
            | ORTHPOL      | see notes    |
            +--------------+--------------+
            
        .. note:: The ORTHPOL polynomials are built up using the "Multiple-Component Discretization Procedure" described in [4]_. The following parameters describing the measure function are required in order to use the procedure for finding the recursion coefficients (alpha,beta) and have to be provided at construction time:
            
                * ``ncapm``: (int) maximum integer N0 (default = 500)
                * ``mc``: (int) number of component intervals in the continuous part of the spectrum
                * ``mp``: (int) number of points in the discrete part of the spectrum. If the measure has no discrete part, set mp=0
                * ``xp``, ``yp``: (Numpy 1d-array) of dimension mp, containing the abscissas and the jumps of the point spectrum
                * ``mu``: (function) measure function that returns the mass (float) with arguments: ``x`` (float) absissa, ``i`` (int) interval number in the continuous part
                * ``irout``: (int) selects the routine for generating the recursion coefficients from the discrete inner product; ``irout=1`` selects the routine ``sti``, ``irout!=1`` selects the routine ``lancz``
                * ``finl``, ``finr``: (bool) specify whether the extreme left/right interval is finite (false for infinite)
                * ``endl``, ``endr``: (Numpy 1d-array) of dimension ``mc`` containing the left and right endpoints of the component intervals. If the first of these extends to -infinity, endl[0] is not being used by the routine.
            Parameters ``iq``, ``quad``, ``idelta`` in [4]_ are suppressed. Instead the routine ``qgp`` of ORTHPOL [4]_ is used by default (``iq=0`` and ``idelta=2``)
            
        """
        
        self.sdout = sdout
        
        # Check consistency of polynomial types and parameters
        if (poly in AVAIL_POLY):
            if (poly == JACOBI):
                if len(params) != 2:
                    raise AttributeError("The number of parameters inserted for the polynomial of type '%s' is not correct" % poly)
                    return
            if ((poly == LAGUERREP) or (poly == LAGUERREF)):
                if len(params) != 1:
                    raise AttributeError("The number of parameters inserted for the polynomial of type '%s' is not correct" % poly)
                    return
            if ((poly == ORTHPOL)):
                if not ORTHPOL_SUPPORT:
                    raise ImportError("The orthpol package is not installed on this machine.")
                if len(params) != 11:
                    print >> self.sdout, "The number of parameters inserted for the polynomial of type '%s' is not correct" % poly
                    return
        else:
            raise AttributeError("The inserted type of polynomial is not available.")
        self.poly = poly
        self.params = params
    
    def __JacobiGQ(self,N):
        """
        Purpose: Compute the N'th order Gauss quadrature points, x, 
                 and weights, w, associated with the Jacobi 
                 polynomial, of type (alpha,beta) > -1 ( <> -0.5).
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __JacobiGQ cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) or AlmostEqual(beta,-0.5) ):
                return self.__JacobiCGQ(N)
            
            x = np.zeros((N+1))
            w = np.zeros((N+1))
            
            if (N == 0):
                x[0] = -(alpha-beta)/(alpha+beta+2)
                w[0] = 2
                return (x,w)
            
            J = np.zeros((N+1,N+1))
            h1 = 2.* np.arange(0.,N+1)+alpha+beta
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                J = np.diag(-1./2.*(alpha**2.-beta**2.)/(h1+2.)/h1) +  np.diag( 2./(h1[0:N] + 2.) * np.sqrt( np.arange(1.,N+1) * (np.arange(1.,N+1)+alpha+beta) * (np.arange(1.,N+1)+alpha) * (np.arange(1.,N+1)+beta) / (h1[0:N] + 1.) / (h1[0:N] + 3.) ) , 1) 
            if (alpha + beta < 10.*np.finfo(np.float64).eps): J[0,0] = 0.0
            J = J + np.transpose(J)
            
            # Compute quadrature by eigenvalue solve
            vals,vecs = LA.eigh(J)
            perm = np.argsort(vals)
            x = vals[perm]
            vecs = vecs[:,perm]
            w = np.power(np.transpose(vecs[0,:]),2.) * 2**(alpha+beta+1.)/(alpha+beta+1.)*gammaF(alpha+1.)*gammaF(beta+1.)/gammaF(alpha+beta+1.)
            return (np.asarray(x),np.asarray(w))
        
    def __JacobiGL(self,N):
        """
        x = JacobiGL
        Purpose: Compute the N'th order Gauss Lobatto quadrature points, x, 
                 and weights, w, associated with the Jacobi 
                 polynomial, of type (alpha,beta) > -1 ( <> -0.5).
        
        .. note:: For the computation of the weights for generic Jacobi polynomials, see [5]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __JacobiGL cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,0.0) or AlmostEqual(beta,0.0) ):
                return self.__JacobiLGL(N)
            elif ( AlmostEqual(alpha,-0.5) or AlmostEqual(beta,-0.5) ):
                return self.__JacobiCGL(N)
            
            x = np.mat(np.zeros((N+1)))
            if ( N == 1 ): 
                x[0] = -1.
                x[1] = 1.
                return x
                
            [xint,wint] = self.__JacobiGQ(N-2)
            x = np.concatenate(([-1.], xint, [1.]))
            w0 = ( 2.**(alpha+beta+1.) * gammaF(alpha+2) * gammaF(beta+1) / gammaF(alpha+beta+3) ) * SPcomb(N+alpha,N-1)/ (SPcomb(N+beta,N-1) * SPcomb(N+alpha+beta+1,N-1))
            wint *= 1./(1.-xint**2.)
            w = np.concatenate(([w0],wint,[w0]))
            return (x,w)
        
    def __JacobiLGL(self,N):
        """
        x,w = JacobiLGL(N)
        Compute the Legendre Gauss Lobatto points and weights for polynomials up
        to degree N
        Algorithm (25) taken from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __JacobiLGL cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else: 
            # Unpack parameters
            alpha,beta = self.params
            if ( not AlmostEqual(alpha,0.0) or not AlmostEqual(beta,0.0) ):
                print >> self.sdout, "The method can be called only for Legendre Polynomials. Actual values of alpha and beta: %f, %f" % (alpha,beta)
            else:
                maxNewtonIter = 1000
                NewtonTOL = 1e-12
                x = np.zeros((N+1))
                w = np.zeros((N+1))
                if ( N == 1 ):
                    x[0] = -1.
                    x[1] = 1.
                    w[0] = 1.
                    w[1] = 1.
                else:
                    x[0] = -1.
                    w[0] = 2./(N * (N + 1.))
                    x[N] = 1.
                    w[N] = w[0]
                    for j in range(1,int(np.floor((N+1.)/2.)-1) + 1):
                        x[j] = -np.cos( (j + 1./4.)*np.pi/N - 3./(8.*N*np.pi) * 1./(j+1./4.) )
                        # Newton iteratio for getting the point
                        k = 0
                        delta = 10. * NewtonTOL
                        while ( (k < maxNewtonIter) and (abs(delta) > NewtonTOL * abs(x[j])) ):
                            k = k + 1
                            q,dq,LN = self.__qLEvaluation(N,x[j])
                            delta = -q/dq
                            x[j] = x[j] + delta
                        q,dq,LN = self.__qLEvaluation(N,x[j])
                        x[N-j] = -x[j]
                        w[j] = 2./(N*(N+1)*LN**2)
                        w[N-j] = w[j]
                if ( np.remainder(N,2) == 0 ):
                    q,dq,LN = self.__qLEvaluation(N,0.)
                    x[N/2] = 0
                    w[N/2] = 2./(N*(N+1)*LN**2)
                return (np.asarray(x),np.asarray(w))
        
    def __JacobiCGQ(self,N):
        """
        Compute the Chebyshev Gauss points and weights for polynomials up
        to degree N
        Algorithm (26) taken from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __JacobiCGQ cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( not AlmostEqual(alpha,-0.5) or not AlmostEqual(beta,-0.5) ):
                print >> self.sdout, "The method can be called only for Chebyshev Polynomials. Actual values of alpha and beta: %f, %f" % (alpha,beta)
            else:
                x = np.zeros((N+1))
                w = np.zeros((N+1))
                for j in range(0,N+1):
                    x[j] = -np.cos( (2.*j + 1.)/(2.*N + 2.) * np.pi )
                    w[j] = np.pi / (N + 1.)
                return (np.asarray(x),np.asarray(w))
        
    def __JacobiCGL(self,N):
        """
        x,w = JacobiCL(N)
        Compute the Chebyshev Gauss Lobatto points and weights for polynomials up
        to degree N
        Algorithm (27) taken from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __JacobiCGL cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( not AlmostEqual(alpha,-0.5) or not AlmostEqual(beta,-0.5) ):
                print >> self.sdout, "The method can be called only for Chebyshev Polynomials. Actual values of alpha and beta: %f, %f" % (alpha,beta)
            else:
                x = np.zeros((N+1))
                w = np.zeros((N+1))
                for j in range(0,N+1):
                    x[j] = -np.cos(float(j)/float(N) * np.pi)
                    w[j] = np.pi/float(N)
                w[0] = w[0]/2.
                w[N] = w[N]/2.
                return (np.asarray(x),np.asarray(w))
        
    def __HermitePGQ(self,N):
        """
        Compute the Hermite-Gauss quadrature points and weights for Hermite Physicists 
        polynomials up to degree N
        For further details see [2]_
        """
        if (self.poly != HERMITEP):
            print >> self.sdout, "The method __HermitePGQ cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            j = np.asarray(range(1,N+1))
            b = np.sqrt(j / 2.)
            D = np.diag(b,1)
            D = D + D.T
            x,vec = np.linalg.eig(D)
            x = np.sort(x)
            hp = self.__HermiteP(x,N)
            w = np.sqrt(np.pi) * 2.**N * factorial(N) / ((N+1) * hp**2.)
            return (x,w)
        
    def __HermiteFGQ(self,N):
        """
        Compute the Hermite-Gauss quadrature points and weights for the Hermite 
        functions up to degree N
        For further details see [2]_
        """
        if (self.poly != HERMITEF):
            print >> self.sdout, "The method __HermiteFGQ cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            j = np.asarray(range(1,N+1))
            b = np.sqrt(j / 2.)
            D = np.diag(b,1)
            D = D + D.T
            x,vec = np.linalg.eig(D)
            hf = self.__HermiteF(x,N)
            w = np.sqrt(np.pi) / ((N+1) * hf**2.)
            return (x,w)
    
    def __HermiteP_Prob_GQ(self,N):
        """
        Compute the Hermite-Gauss quadrature points and weights for Hermite 
        Probabilistic polynomials up to degree N
        For further details see Golub-Welsh algorithm in [3]
        """
        if (self.poly != HERMITEP_PROB):
            print >> self.sdout, "The method __HermiteP_Prob_GQ cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            j = np.asarray(range(1,N+1))
            b = np.sqrt(j)
            D = np.diag(b,1)
            D = D + D.T
            x,vec = np.linalg.eig(D)
            x = np.sort(x)
            hp = self.__HermiteP_Prob(x,N)
            w = factorial(N) / ((N+1) * hp**2.)
            return (x,w)
    
    def __LaguerrePGQ(self,N,alpha=None):
        """
        __LaguerrePGQ(): Compute the Laguerre-Gauss quadrature points and weights for Laguerre polynomials up to degree N
        
        Syntax:
            ``(x,w) = __LaguerrePGQ(N,[alpha=None])``
        
        Input:
            * ``N`` = (int) Order of polynomial accuracy
            * ``alpha`` = (optional,float) Laguerre constant
        
        Output:
            * ``x`` = set of Laguerre-Gauss quadrature points
            * ``w`` = set of Laguerre-Gauss quadrature weights
        
        .. note:: For further details see [2]_
        """
        if (self.poly != LAGUERREP):
            print >> self.sdout, "The method __LaguerrePGQ cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha is None):
                (alpha,) = self.params
            # Compute points and weights
            j = np.asarray(range(0,N+1))
            a = 2. * j + alpha + 1.
            b = - np.sqrt( j[1:] * (j[1:] + alpha) )
            D = np.diag(b,1)
            D = D + D.T
            D = D + np.diag(a,0)
            x,vec = np.linalg.eig(D)
            x = np.sort(x)
            lp = self.__LaguerreP(x,N).ravel()
            w = gammaF(N+alpha+1.)/ ((N+alpha+1.) * factorial(N+1)) * ( x / lp**2. )
            return (x,w)
    
    def __LaguerreFGQ(self,N,alpha=None):
        """
        __LaguerreFGQ(): Compute the Laguerre-Gauss quadrature points and weights for Laguerre functions up to degree N
        
        Syntax:
            ``(x,w) = __LaguerreFGQ(N,[alpha=None])``
        
        Input:
            * ``N`` = (int) Order of polynomial accuracy
            * ``alpha`` = (optional,float) Laguerre constant
        
        Output:
            * ``x`` = set of Laguerre-Gauss quadrature points
            * ``w`` = set of Laguerre-Gauss quadrature weights
        
        .. note:: For further details see [2]_
        """
        if (self.poly != LAGUERREF):
            print >> self.sdout, "The method __LaguerreFGQ cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha is None):
                (alpha,) = self.params
            # Compute points and weights
            j = np.asarray(range(0,N+1))
            a = 2. * j + alpha + 1.
            b = - np.sqrt( j[1:] * (j[1:] + alpha) )
            D = np.diag(b,1)
            D = D + D.T
            D = D + np.diag(a,0)
            x,vec = np.linalg.eig(D)
            x = np.sort(x)
            lf = self.__LaguerreF(x,N).ravel()
            w = gammaF(N+alpha+1.)/ ((N+alpha+1.) * factorial(N+1)) * ( x / lf**2. )
            return (x,w)
    
    def __LaguerrePGR(self,N,alpha=None):
        """
        __LaguerrePGR(): Compute the Laguerre-Gauss-Radau quadrature points and weights for Laguerre polynomials up to degree N
        
        Syntax:
            ``(x,w) = __LaguerrePGR(N,[alpha=None])``
        
        Input:
            * ``N`` = (int) Order of polynomial accuracy
            * ``alpha`` = (optional,float) Laguerre constant
        
        Output:
            * ``x`` = set of Laguerre-Gauss-Radau quadrature points
            * ``w`` = set of Laguerre-Gauss-Radau quadrature weights
        
        .. note:: For further details see [2]_
        """
        if (self.poly != LAGUERREP):
            print >> self.sdout, "The method __LaguerrePGR cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha is None):
                (alpha,) = self.params
            # Compute points and weights x1...xN, w1...wN
            j = np.asarray(range(0,N))
            a = 2. * j + (alpha+1.) + 1.
            b = - np.sqrt( j[1:] * (j[1:] + (alpha+1.) ) )
            D = np.diag(b,1)
            D = D + D.T
            D = D + np.diag(a,0)
            x,vec = np.linalg.eig(D)
            x = np.sort(x)
            lp = self.__LaguerreP(x,N).ravel()
            w = gammaF(N+alpha+1.)/ ((N+alpha+1.) * factorial(N)) * ( 1. / lp**2. )
            # Add x0 and w0
            x = np.hstack((0.0,x))
            w0 = (alpha+1.) * gammaF(alpha+1.)**2. * gammaF(N+1) / gammaF(N+alpha+2.)
            w = np.hstack((w0,w))
            return (x,w)
    
    def __LaguerreFGR(self,N,alpha=None):
        """
        __LaguerreFGR(): Compute the Laguerre-Gauss-Radau quadrature points and weights for Laguerre functions up to degree N
        
        Syntax:
            ``(x,w) = __LaguerreFGR(N,[alpha=None])``
        
        Input:
            * ``N`` = (int) Order of polynomial accuracy
            * ``alpha`` = (optional,float) Laguerre constant
        
        Output:
            * ``x`` = set of Laguerre-Gauss-Radau quadrature points
            * ``w`` = set of Laguerre-Gauss-Radau quadrature weights
        
        .. note:: For further details see [2]_
        """
        if (self.poly != LAGUERREF):
            print >> self.sdout, "The method __LaguerreFGR cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha is None):
                (alpha,) = self.params
            # Compute points and weights x1...xN, w1...wN
            j = np.asarray(range(0,N))
            a = 2. * j + (alpha+1.) + 1.
            b = - np.sqrt( j[1:] * (j[1:] + (alpha+1.) ) )
            D = np.diag(b,1)
            D = D + D.T
            D = D + np.diag(a,0)
            x,vec = LA.eig(D)
            x = np.sort(x)
            lp = self.__LaguerreF(x,N).ravel()
            w = gammaF(N+alpha+1.)/ ((N+alpha+1.) * factorial(N)) * ( 1. / lp**2. )
            # Add x0 and w0
            x = np.hstack((0.0,x))
            w0 = (alpha+1.) * gammaF(alpha+1.)**2. * gammaF(N+1) / gammaF(N+alpha+2.)
            w = np.hstack((w0,w))
            return (x,w)
    
    def __ORTHPOL_GQ(self,N):
        """
        __ORTHPOL_GQ(): Compute the ORTHPOL Gauss quadrature points and weights for a generic measure functions up to degree N
        
        Syntax:
            ``(x,w,ierr) = __ORTHPOL_GQ(N)``
        
        Input:
            * ``N`` = (int) Order of polynomial accuracy
        
        Output:
            * ``x`` = set of Gauss quadrature points
            * ``w`` = set of Gauss quadrature weights
            * ``ierr`` = (int) error flag equal to 0 on normal return, equal to ``i`` if the QR algorithm does not converge within 30 iterations on evaluating the ``i``-th eigenvalue, equal to -1 if ``N`` is not in range and equal to -2 if one of the ``beta`` is negative.
        
        .. note:: For further details see [4]_
        """
        if not ORTHPOL_SUPPORT:
            raise ImportError("The orthpol package is not installed on this machine.")

        eps = orthpol.d1mach(3)
        
        # Unpack params
        ncapm = self.params[0]
        mc =    self.params[1]
        mp =    self.params[2]
        xp =    self.params[3]
        yp =    self.params[4]
        mu =    self.params[5]
        irout = self.params[6]
        finl =  self.params[7]
        finr =  self.params[8]
        endl =  self.params[9]
        endr =  self.params[10]
        # Default values
        iq = 0
        idelta = 2
        # Compute the alpha and beta coeff.
        (alphaCap, betaCap, ncapCap, kountCap, ierrCap, ieCap) = orthpol.dmcdis(N+1, ncapm, mc, mp, xp, yp, mu, eps, iq, idelta, irout, finl, finr, endl, endr )
        # Compute Gauss quadrature points and weights
        (xg,wg,ierr) = orthpol.dgauss(N+1,alphaCap,betaCap,eps);
        
        return (xg,wg,ierr)
    
    def __ORTHPOL_GL(self,N,left,right):
        """
        __ORTHPOL_GL(): Compute the ORTHPOL Gauss-Lobatto quadrature points and weights for a generic measure functions up to degree N
        
        Syntax:
            ``(x,w,ierr) = __ORTHPOL_GL(N,left,right)``
        
        Input:
            * ``N`` = (int) Order of polynomial accuracy
            * ``left`` = (optional,float) containing the left endpoint
            * ``right`` = (optional,float) containing the right endpoint
        
        Output:
            * ``x`` = set of Gauss-Lobatto quadrature points
            * ``w`` = set of Gauss-Lobatto quadrature weights
            * ``ierr`` = (int) error flag equal to 0 on normal return, equal to ``i`` if the QR algorithm does not converge within 30 iterations on evaluating the ``i``-th eigenvalue, equal to -1 if ``N`` is not in range and equal to -2 if one of the ``beta`` is negative.
        
        .. note:: For further details see [4]_
        """
        
        if not ORTHPOL_SUPPORT:
            raise ImportError("The orthpol package is not installed on this machine.")

        eps = orthpol.d1mach(3)
        
        # Unpack params
        ncapm = self.params[0]
        mc =    self.params[1]
        mp =    self.params[2]
        xp =    self.params[3]
        yp =    self.params[4]
        mu =    self.params[5]
        irout = self.params[6]
        finl =  self.params[7]
        finr =  self.params[8]
        endl =  self.params[9]
        endr =  self.params[10]
        # Default values
        iq = 0
        idelta = 2
        # Compute the alpha and beta coeff.
        (alphaCap, betaCap, ncapCap, kountCap, ierrCap, ieCap) = orthpol.dmcdis(N, ncapm, mc, mp, xp, yp, mu, eps, iq, idelta, irout, finl, finr, endl, endr )
        # Compute Gauss quadrature points and weights
        (xg,wg,ierr) = orthpol.dlob(N, alphaCap, betaCap, left, right);
        
        return (xg,wg,ierr)
    
    
    def __ORTHPOL_GR(self,N,end):
        """
        __ORTHPOL_GR(): Compute the ORTHPOL Gauss-Radau quadrature points and weights for a generic measure functions up to degree N
        
        Syntax:
            ``(x,w,ierr) = __ORTHPOL_GR(N,end)``
        
        Input:
            * ``N`` = (int) Order of polynomial accuracy
            * ``end`` = (optional,float) containing the endpoint
        
        Output:
            * ``x`` = set of Gauss-Lobatto quadrature points
            * ``w`` = set of Gauss-Lobatto quadrature weights
            * ``ierr`` = (int) error flag equal to 0 on normal return, equal to ``i`` if the QR algorithm does not converge within 30 iterations on evaluating the ``i``-th eigenvalue, equal to -1 if ``N`` is not in range and equal to -2 if one of the ``beta`` is negative.
        
        .. note:: For further details see [4]_
        """

        if not ORTHPOL_SUPPORT:
            raise ImportError("The orthpol package is not installed on this machine.")
        
        eps = orthpol.d1mach(3)
        
        # Unpack params
        ncapm = self.params[0]
        mc =    self.params[1]
        mp =    self.params[2]
        xp =    self.params[3]
        yp =    self.params[4]
        mu =    self.params[5]
        irout = self.params[6]
        finl =  self.params[7]
        finr =  self.params[8]
        endl =  self.params[9]
        endr =  self.params[10]
        # Default values
        iq = 0
        idelta = 2
        # Compute the alpha and beta coeff.
        (alphaCap, betaCap, ncapCap, kountCap, ierrCap, ieCap) = orthpol.dmcdis(N, ncapm, mc, mp, xp, yp, mu, eps, iq, idelta, irout, finl, finr, endl, endr )
        # Compute Gauss quadrature points and weights
        (xg,wg,ierr) = orthpol.dradau(N, alphaCap, betaCap, end);
        
        return (xg,wg,ierr)

    def Quadrature(self, N, quadType=None, normed=False, left=None, right=None, end=None):
        """
        Quadrature(): Generates list of nodes and weights for the ``quadType`` quadrature rule using the selected Polynomial basis
        
        Syntax:
            ``(x,w) = Quadrature(N, [quadType=None], [normed=False], [left=None], [right=None], [end=None])``
        
        Input:
            * ``N`` = (int) accuracy level required
            * ``quadType`` = (``AVAIL_POLYS``) type of quadrature to be used. Default is Gauss quadrature rule.
            * ``normed`` = (optional,bool) whether the weights will be normalized or not
            * ``left`` = (optional,float) containing the left endpoint (used by ORTHPOL Gauss-Lobatto rules)
            * ``right`` = (optional,float) containing the right endpoint (used by ORTHPOL Gauss-Lobatto rules)
            * ``end`` = (optional,float) containing the endpoint (used by ORTHPOL Gauss-Radau rules)
        
        Output:
            * ``x`` = (1d-array,float) containing the nodes
            * ``w`` = (1d-array,float) containing the weights
        """
        if (quadType == None) or (quadType == GAUSS):
            return self.GaussQuadrature(N, normed)
        elif quadType == GAUSSLOBATTO:
            return self.GaussLobattoQuadrature(N,normed,left,right)
        elif quadType == GAUSSRADAU:
            return self.GaussRadauQuadrature(N,normed,end)
        elif quadType in AVAIL_QUADPOINTS:
            if self.poly == HERMITEP_PROB and (quadType in [GQN,KPN]):
                if quadType == GQN: return gqn(N)
                if quadType == KPN: return kpn(N)
            if self.poly == JACOBI and (quadType in [GQU,KPU,CC,FEJ]):
                if quadType == GQU: return gqu(N,norm=normed)
                if quadType == KPU: return kpu(N,norm=normed)
                if quadType == CC:  return cc(N,norm=normed)
                if quadType == FEJ: return fej(N,norm=normed)
                
        else:
            raise AttributeError("The selected type of quadrature rule is not available")
    
    def GaussQuadrature(self,N,normed=False):
        """
        GaussQuadrature(): Generates list of nodes and weights for the Gauss quadrature rule using the selected Polynomial basis
        
        Syntax:
            ``(x,w) = GaussQuadrature(N,[normed=False])``
        
        Input:
            * ``N`` = (int) accuracy level required
            * ``normed`` = (optional,bool) whether the weights will be normalized or not
        
        Output:
            * ``x`` = (1d-array,float) containing the nodes
            * ``w`` = (1d-array,float) containing the weights
        """
        if (self.poly == JACOBI):
            (x,w) = self.__JacobiGQ(N)
        elif (self.poly == HERMITEP):
            (x,w) = self.__HermitePGQ(N)
        elif (self.poly == HERMITEF):
            (x,w) = self.__HermiteFGQ(N)
        elif (self.poly == HERMITEP_PROB):
            (x,w) = self.__HermiteP_Prob_GQ(N)
        elif (self.poly == LAGUERREP):
            (x,w) = self.__LaguerrePGQ(N)
        elif (self.poly == LAGUERREF):
            (x,w) = self.__LaguerreFGQ(N)
        elif (self.poly == ORTHPOL):
            (x,w,ierr) = self.__ORTHPOL_GQ(N)
            if ierr != 0:
                print >> self.sdout, "Error in ORTHPOL GaussQuadrature."
        
        if normed:
            w = w / np.sum(w)
        
        return (x,w.flatten())
            
    def GaussLobattoQuadrature(self,N,normed=False,left=None,right=None):
        """
        GaussLobattoQuadrature(): Generates list of nodes for the Gauss-Lobatto quadrature rule using selected Polynomial basis
        
        Syntax:
            ``x = GaussLobattoQuadrature(N,[normed=False],[left=None],[right=None])``
        
        Input:
            * ``N`` = (int) accuracy level required
            * ``normed`` = (optional,bool) whether the weights will be normalized or not
            * ``left`` = (optional,float) containing the left endpoint (used by ORTHPOL)
            * ``right`` = (optional,float) containing the right endpoint (used by ORTHPOL)            
        
        Output:
            * ``x`` = (1d-array,float) containing the nodes
            * ``w`` = (1d-array,float) containing the weights
        
        .. note:: Available only for Jacobi Polynomials and ORTHPOL
        """
        if (self.poly == JACOBI):
            (x,w) = self.__JacobiGL(N)
        elif (self.poly == ORTHPOL):
            (x,w,ierr) = self.__ORTHPOL_GL(N,left,right)
            if ierr != 0:
                print >> self.sdout, "Error in ORTHPOL GaussLobattoQuadrature."
        else:
            print >> self.sdout, "Gauss Lobatto quadrature does not apply to the selected Polynomials/Function."
        
        if normed:
            w = w / np.sum(w)
        
        return (x,w.flatten())
        
    
    def GaussRadauQuadrature(self,N,normed=False,end=None):
        """
        GaussRadauQuadrature(): Generates list of nodes for the Gauss-Radau quadrature rule using selected Polynomial basis
        
        Syntax:
            ``x = GaussRadauQuadrature(N,[normed=False],[end=None])''
        
        Input:
            * ``N'' = (int) accuracy level required
            * ``normed`` = (optional,bool) whether the weights will be normalized or not
            * ``end`` = (optional,float) containing the endpoint (used by ORTHPOL)
        
        Output:
            * ``x'' = (1d-array,float) containing the nodes
            * ``w'' = (1d-array,float) weights
        
        .. note:: Available only for Laguerre Polynomials/Functions and ORTHPOL
        """
        if (self.poly == LAGUERREP):
            (x,w) = self.__LaguerrePGR(N)
        elif (self.poly == LAGUERREF):
            (x,w) = self.__LaguerreFGR(N)
        elif (self.poly == ORTHPOL):
            (x,w,ierr) = self.__ORTHPOL_GR(N,end)
            if ierr != 0:
                print >> self.sdout, "Error in ORTHPOL GaussRadauQuadrature."
        else:
            print >> self.sdout, "Gauss Lobatto quadrature does not apply to the selected Polynomials/Function."
        
        if normed:
            w = w / np.sum(w)
        
        return (x,w.flatten())
        
    def __qLEvaluation(self,N,x):
        """
        q,dq,LN = qLEvaluation(N,x)
        Evaluate Legendre Polynomial LN and 
        q = L_N+1 - L_N-1
        q' = L'_N+1 - L'_N-1
        at point x.
        Algorithm (24) taken from [1]_
        """
        L = np.zeros((N+2))
        DL = np.zeros((N+2))
        L[0] = 1.
        L[1] = x
        DL[0] = 0.
        DL[1] = 1.
        for k in range(2,N+2):
            L[k] = (2.*k-1.)/k * x * L[k-1] - (k-1.)/k * L[k-2]
            DL[k] = DL[k-2] + (2.*k-1.) * L[k-1]
        q = L[N+1] - L[N-1]
        dq = DL[N+1] - DL[N-1]
        return (q,dq,L[N])

    def __JacobiP(self,x,N,alpha=None,beta=None):

        if (self.poly != JACOBI):
            print >> self.sdout, "The method __JacobiP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (alpha is None) and (beta is None):
                # Unpack parameters
                alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
                return self.__ChebyshevP(x,N)
            else:
                if ORTHPOL_SUPPORT:
                    (al,be,ierr) = orthpol.drecur(N+1,6,alpha,beta)
                    v = orthpol.polyeval(x,N,al,be)
                    return v
                else:
                    PL = np.zeros((N+1,len(x)))
                    gamma0 = 2**(alpha+beta+1)/(alpha+beta+1)*gammaF(alpha+1)*gammaF(beta+1)/gammaF(alpha+beta+1)
                    PL[0,:] = 1.0/np.sqrt(gamma0)
                    if (N == 0): return PL[0,:]
                    gamma1 = (alpha+1.)*(beta+1.)/(alpha+beta+3.)*gamma0
                    PL[1,:] = ((alpha+beta+2.)*x/2. + (alpha-beta)/2.)/np.sqrt(gamma1)
                    if (N == 1): return PL[N,:]
                    # Recurrence
                    aold = 2./(2.+alpha+beta)*np.sqrt((alpha+1.)*(beta+1.)/(alpha+beta+3.))
                    for i in range(1,N):
                        h1 = 2.*i+alpha+beta
                        anew = 2./(h1+2.)*np.sqrt( (i+1.)*(i+1.+alpha+beta)*(i+1.+alpha)*(i+1.+beta)/(h1+1.)/(h1+3.) )
                        bnew = - (alpha**2. - beta**2.)/h1/(h1+2.)
                        PL[i+1,:] = 1.0 / anew*( -aold*PL[i-1,:] + np.multiply((x-bnew),PL[i,:]) )
                        aold = anew
                    
                    return PL[N,:]
            
    def __LegendreP(self,r, N):
        """
        P = LegendreP(r,N)
        Returns an 1d-array with the Legendre polynomial of order N at points r.
        This calls JacobiP(r,0.,0.,N)
        Note: normalized to be orthonormal        
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __LegendreP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,0.0) and AlmostEqual(beta,0.0) ):
                return self.__JacobiP(r,N,0.,0.)
        
    def __ChebyshevP(self,r, N):
        """
        T = ChebyshevP(r, N)
        Returns an 1d-array with the Chebyshev (first type) polynomial
        of order N at points r
        Algorithm (21) taken from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __ChebyshevP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
                # shape r
                Ks = 50
                rShape = r.shape
                if ( N == 0 ): return np.ones(rShape)
                if ( N == 1 ): return r
                if ( N <= Ks):
                    T2 = np.ones(rShape)
                    T1 = r
                    for j in range(2,N+1):
                        T = 2 * r *  T1 - T2
                        T2 = T1
                        T1 = T
                else:
                    T = np.cos(N * np.arccos(r) )
                return T
        
    def __HermiteP(self,r, N):
        """
        Returns the N-th Hermite Physicist polynomial using the recurrence relation
        """
        if (self.poly != HERMITEP):
            print >> self.sdout, "The method __HermiteP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            old2 = np.ones( len(r) )
            if (N == 0):
                return old2
            old1 = 2. * r
            if (N == 1):
                return old1
            new = 2. * r * old1 - 2. * old2
            for i in xrange(3,N+1):
                old2 = old1
                old1 = new
                new = 2. * r * old1 - 2. * (i-1) * old2
            return new
    
    def __HermitePnorm(self,r, N):
        """
        Returns the N-th Hermite Physicist normalized polynomial using the 
        recurrence relation in [3]
        """
        if (self.poly != HERMITEP):
            print >> self.sdout, "The method __HermitePnorm cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            old2 = np.zeros( len(r) )
            if (N == -1):
                return old2
            old1 = np.ones( len(r) ) / (np.pi**(1./4.))
            if (N == 0):
                return old1
            new = np.sqrt(2) * r * old1
            for i in xrange(2,N+1):
                old2 = old1
                old1 = new
                new = np.sqrt(2./i) * r * old1 - np.sqrt((i-1.)/i) * old2
            return new
        
    def __HermiteF(self,r, N):
        """
        Returns the N-th Hermite function using the recurrence relation
        Reference: [2]
        """
        if (self.poly != HERMITEF):
            print >> self.sdout, "The method __HermiteF cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            old2 = np.exp(-r**2. / 2.)
            if (N == 0):
                return old2
            old1 = np.sqrt(2.) * r * np.exp(-r**2. / 2.)
            if (N == 1):
                return old1
            new = r *  old1 - np.sqrt(1./2.) * old2
            for i in xrange(3,N+1):
                old2 = old1
                old1 = new
                new = r * np.sqrt(2./i) * old1 - np.sqrt((i-1)/i) * old2
            return new
    
    def __HermiteP_Prob(self,r, N):
        """
        Returns the N-th Hermite Probabilistic polynomial using the recurrence relation
        Use the Probabilistic Hermite Polynomial
        """
        if (self.poly != HERMITEP_PROB):
            print >> self.sdout, "The method __HermiteP_Prob cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            old2 = np.ones( len(r) )
            if (N == 0):
                return old2
            old1 = r.copy()
            if (N == 1):
                return old1
            new = r * old1 - old2
            for i in xrange(3,N+1):
                old2 = old1
                old1 = new
                new = r * old1 - (i-1) * old2
            return new
        
    def __LaguerreP(self,r,N,alpha=None):
        """
        __LaguerreP(): Generates the N-th Laguerre polynomial using the recurrence relation
        
        Syntax:
            ``__LaguerreP(r,N,[alpha=None])``
        
        Input:
            * ``r`` = (1d-array,float) set of points
            * ``N`` = (int) Polynomial order
            * ``alpha`` = (optional,float) Laguerre parameter
        
        Output:
            * ``P`` = (1d-array,float) ``N``-th Laguerre polynomial evaluated on ``r``
        """
        
        if (self.poly != LAGUERREP):
            print >> self.sdout, "The method __LaguerreP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha == None):
                (alpha,) = self.params
            # Recurrence relation
            old2 = np.ones( len(r) )
            if (N == 0):
                return old2
            old1 = alpha + 1. - r
            if (N == 1):
                return old1
            new = ( (3. + alpha - r) * old1 - (1. + alpha) * old2 ) / 2.0
            for i in xrange(3,N+1):
                n = i - 1.
                old2 = old1
                old1 = new
                new = ( (2*n + alpha + 1. - r) * old1 - (n + alpha) * old2 ) / (n + 1.)
            return new
    
    def __LaguerreF(self,r,N,alpha=None):
        """
        __LaguerreF(): Generates the N-th Laguerre function using the recurrence relation
        
        Syntax:
            ``__LaguerreF(r,N,[alpha=None])``
        
        Input:
            * ``r`` = (1d-array,float) set of points
            * ``N`` = (int) Polynomial order
            * ``alpha`` = (optional,float) Laguerre parameter
        
        Output:
            * ``P`` = (1d-array,float) ``N``-th Laguerre function evaluated on ``r``
        """
        
        if (self.poly != LAGUERREF):
            print >> self.sdout, "The method __LaguerreF cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha == None):
                (alpha,) = self.params
            # Recurrence relation
            old2 = np.exp(-r/2.)
            if (N == 0):
                return old2
            old1 = (alpha + 1. - r) * np.exp(-r/2.)
            if (N == 1):
                return old1
            new = ( (3. + alpha - r) * old1 - (1. + alpha) * old2 ) / 2.0
            for i in xrange(3,N+1):
                n = i - 1.
                old2 = old1
                old1 = new
                new = ( (2*n + alpha + 1. - r) * old1 - (n + alpha) * old2 ) / (n + 1.)
            return new
    
    def __GradLaguerreP(self,r,N,k,alpha=None):
        """
        __GradLaguerreP(): Generates the k-th derivative of the N-th Laguerre polynomial using the recurrence relation
        
        Syntax:
            ``__LaguerreP(r,N,k,[alpha=None])``
        
        Input:
            * ``r`` = (1d-array,float) set of points
            * ``N`` = (int) Polynomial order
            * ``k`` = (int) derivative order
            * ``alpha`` = (optional,float) Laguerre parameter
        
        Output:
            * ``P`` = (1d-array,float) ``k``-th derivative of the ``N``-th Laguerre polynomial evaluated on ``r``
        """
        
        if (self.poly != LAGUERREP):
            print >> self.sdout, "The method __LaguerreP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha == None):
                (alpha,) = self.params
            if (k == 0):
                dP = self.__LaguerreP(r,N,alpha)
            else:
                if (N == 0):
                    dP = np.zeros(r.shape)
                else:
                    dP = - self.__GradLaguerreP(r,N-1,k-1,alpha+1.)
            return dP
    
    def __GradLaguerreF(self,r,N,k,alpha=None):
        """
        __GradLaguerreF(): Generates the k-th derivative of the N-th Laguerre function using the recurrence relation
        
        Syntax:
            ``__LaguerreF(r,N,k,[alpha=None])``
        
        Input:
            * ``r`` = (1d-array,float) set of points
            * ``N`` = (int) Polynomial order
            * ``k`` = (int) derivative order
            * ``alpha`` = (optional,float) Laguerre parameter
        
        Output:
            * ``P`` = (1d-array,float) ``k``-th derivative of the ``N``-th Laguerre function evaluated on ``r``
        """
        
        if (self.poly != LAGUERREF):
            print >> self.sdout, "The method __LaguerreF cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            if (alpha == None):
                (alpha,) = self.params
            if (k == 0):
                dP = self.__LaguerreF(r,N,alpha)
            else:
                if (N == 0):
                    dP = -0.5 * self.__GradLaguerreF(r,N,k-1,alpha)
                else:
                    dP = - self.__GradLaguerreF(r,N-1,k-1,alpha+1.) - 0.5 * self.__GradLaguerreF(r,N,k-1,alpha)
            return dP
    
    def __GradHermiteP(self,r,N,k):
        """
        Compute the first derivative of the N-th Hermite Physicist Polynomial 
        using the recursion relation in [2]
        """
        if (self.poly != HERMITEP):
            print >> self.sdout, "The method __GradHermiteP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (k == 0):
                dP = self.__HermiteP(r,N)
            else:
                if (N == 0):
                    dP = np.zeros(r.shape)
                else:
                    dP = 2. * N * self.__GradHermiteP(r,N-1,k-1)
            return dP
            
    def __GradHermitePnorm(self,r,N,k):
        """
        Compute the first derivative of the N-th Hermite Physicist Normalized Polynomial 
        using the recursion relation in [3]
        """
        if (self.poly != HERMITEP):
            print >> self.sdout, "The method __GradHermitePnorm cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (k == 0):
                dP = self.__HermitePnorm(r,N)
            else:
                if (N == 0):
                    dP = np.zeros(r.shape)
                else:
                    dP = np.sqrt(2.*N) * self.__GradHermitePnorm(r,N-1,k-1)
            return dP
        
    def __GradHermiteF(self,r,N,k):
        """
        Compute the first derivative of the N-th Hermite Function using the
        recursion relation in [2]
        """
        if (self.poly != HERMITEF):
            print >> self.sdout, "The method __GradHermiteF cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (k == 0):
                dP = self.__HermiteF(r,N)
            else:
                if (N == 0):
                    # Compute the derivative of the first Hermite function using
                    # direct derivatives (See formula in the notes)
                    mat = np.zeros((k+1,k+1))
                    mat[0,0] = 1
                    for i in range(1,k+1):
                        for j in range(np.remainder(i,2),k+1,2):
                            if (j != 0):
                                mat[i,j] = mat[i,j] - mat[i-1,j-1]
                            if (j < i):
                                mat[i,j] = mat[i,j] + mat[i-1,j+1] * (j+1)
                    dP = np.zeros(r.shape)
                    for i in range(0,k+1):
                        dP = dP + mat[-1,i] * r**i * np.exp(-r**2./2.)
                else:
                    dP = np.sqrt(N/2.) * self.__GradHermiteF(r,N-1,k-1) - np.sqrt((N+1.)/2.) * self.__GradHermiteF(r,N+1,k-1)
            return dP
    
    def __GradHermiteP_Prob(self,r,N,k):
        """
        Compute the k-th derivative of the N-th Hermite Probabilistic Polynomial
        """
        if (self.poly != HERMITEP_PROB):
            print >> self.sdout, "The method __GradHermiteP_Prob cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (k == 0):
                dP = self.__HermiteP_Prob(r,N)
            else:
                if (N == 0):
                    dP = np.zeros(r.shape)
                else:
                    dP = N * self.__GradHermiteP_Prob(r,N-1,k-1)
            return dP
    
    def __GradJacobiP(self,r, N, k):
        """
        dP = GradJacobiP(r, alpha, beta, N);
        Purpose: Evaluate the kth-derivative of the Jacobi polynomial of type (alpha,beta)>-1,
        at points r for order N and returns dP[1:length(r))]
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __GradJacobiP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
                return self.__GradChebyshevP(r, N, k, 0)
            else:
                r = np.array(r)
                if (N >= k):
                    dP = gammaF(alpha+beta+N+1.+k)/(2.**k * gammaF(alpha+beta+N+1.)) * np.sqrt(self.__GammaJacobiP(N-k,alpha+k,beta+k)/self.__GammaJacobiP(N,alpha,beta)) * self.__JacobiP(r,N-k,alpha+k,beta+k)
                else:
                    dP = np.zeros(r.shape)
                return dP
    
    def __GradChebyshevP(self,r, N, k, method=0):
        """
        dP = GradChebyshevP(r,N,k,method)
        Returns the k-th derivative of the Chebyshev polynomial of order N at
        points r.
        Method: 0 -> Matrix multiplication
                1 -> Fast Chebyshev Transform
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __GradChebyshevP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
                dP = np.zeros((N+1))
                if ( k == 0 ):
                    dP = self.__ChebyshevP(r,N)
                elif ( method == 0 ):
                    D = self.PolynomialDerivativeMatrix(r,k)
                    P = self.__ChebyshevP(r,N)
                    dP = np.dot(D,P)
                return dP
    
    def __ORTHPOL(self,r,N,k=0):
        """
        dP = GradORTHPOL(r,N,k)
        Returns the 0-th derivative of the N-th orthogonal polynomial defined for the supplied measure
        
        .. note:: For further information see [4]_
        """
        if not ORTHPOL_SUPPORT:
            raise ImportError("The orthpol package is not installed on this machine.")

        eps = orthpol.d1mach(3)
        
        # Unpack params
        ncapm = self.params[0]
        mc =    self.params[1]
        mp =    self.params[2]
        xp =    self.params[3]
        yp =    self.params[4]
        mu =    self.params[5]
        irout = self.params[6]
        finl =  self.params[7]
        finr =  self.params[8]
        endl =  self.params[9]
        endr =  self.params[10]
        # Default values
        iq = 0
        idelta = 2
        # Compute the alpha and beta coeff.
        (alphaCap, betaCap, ncapCap, kountCap, ierrCap, ieCap) = orthpol.dmcdis(N, ncapm, mc, mp, xp, yp, mu, eps, iq, idelta, irout, finl, finr, endl, endr )
        # Evaluate Polynomial
        rs = np.reshape(r,(len(r),1))
        if N >= 0:
            new = np.ones(rs.shape)
        if N >= 1:
            old1 = new
            new = (rs - alphaCap[0])
        for i in range(2,N+1):
            old2 = old1
            old1 = new
            new = (rs - alphaCap[i-1]) * old1 - betaCap[i-1] * old2
        
        return new
    
    
    def GradEvaluate(self,r,N,k,norm=True):
        """
        GradEvaluate(): evaluate the ``k``-th derivative of the ``N``-th order polynomial at points ``r``
        
        Syntax:
            ``P = GradEvaluate(r,N,k[,norm=True])``
        
        Input:
            * ``r`` = (1d-array,float) set of points on which to evaluate the polynomial
            * ``N`` = (int) order of the polynomial
            * ``k`` = (int) order of the derivative
            * ``norm`` = (bool) whether to return normalized (True) or non normalized (False) polynomials
        
        Output:
            * ``P`` = Polynomial evaluated on ``r``
        """
        if (self.poly == JACOBI):
            p = self.__GradJacobiP(r,N,k)
        elif (self.poly == HERMITEP):
            p = self.__GradHermiteP(r,N,k)
        elif (self.poly == HERMITEF):
            p = self.__GradHermiteF(r,N,k)
        elif (self.poly == HERMITEP_PROB):
            p = self.__GradHermiteP_Prob(r,N,k)
        elif (self.poly == LAGUERREP):
            p = self.__GradLaguerreP(r,N,k)
        elif (self.poly == LAGUERREF):
            p = self.__GradLaguerreF(r,N,k)
        elif (self.poly == ORTHPOL):
            if k != 0:
                print >> self.sdout, "Spectral1D: Error. Derivatives of Polynomials obtained using ORTHPOL package are not implemented"
                return
            p = self.__ORTHPOL(r,N).flatten()
        
        if (self.poly == JACOBI):
            if not norm:
                p *= math.sqrt(self.Gamma(N))
        else:
            if norm:
                p /= math.sqrt(self.Gamma(N))
        
        return p
    
    def __GammaLaguerreF(self,N,alpha=None):
        """
        __GammaLaguerreF(): evaluate the normalization constant for the ``N``-th order Laguerre function
        
        Syntax:
            ``g = __GammaLaguerreF(N,[alpha=None])``
        
        Input:
            * ``N`` = (int) order of the polynomial
            * ``alpha'' = (optional,float) Laguerre constant
        
        Output:
            * ``g`` = Normalization constant
        """
        if (self.poly != LAGUERREF):
            print >> self.sdout, "The method __GammaLaguerreF cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (alpha is None):
                # Unpack parameters
                (alpha,) = self.params
            g = gammaF(N+alpha+1.)/gammaF(N+1)
            return g
    
    def __GammaLaguerreP(self,N,alpha=None):
        """
        __GammaLaguerreP(): evaluate the normalization constant for the ``N``-th order Laguerre polynomial
        
        Syntax:
            ``g = __GammaLaguerreP(N,[alpha=None])``
        
        Input:
            * ``N`` = (int) order of the polynomial
            * ``alpha`` = (optional,float) Laguerre constant
        
        Output:
            * ``g`` = Normalization constant
        """
        if (self.poly != LAGUERREP):
            print >> self.sdout, "The method __GammaLaguerreP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (alpha is None):
                # Unpack parameters
                (alpha,) = self.params
            g = gammaF(N+alpha+1.)/gammaF(N+1)
            return g
        
    def __GammaJacobiP(self,N,alpha=None,beta=None):
        """
        gamma = GammaJacobiP(alpha,beta,N)
        Generate the normalization constant for the
        Jacobi Polynomial (alpha,beta) of order N.
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method __GammaJacobiP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            if (alpha is None) and (beta is None):
                # Unpack parameters
                alpha,beta = self.params
            g = 2**(alpha+beta+1.) * (gammaF(N+alpha+1.)*gammaF(N+beta+1.)) / (factorial(N,exact=True) * (2.*N + alpha + beta + 1.)*gammaF(N+alpha+beta+1.))
            return g
        
    def __GammaHermiteP(self,N):
        """
        Returns the normalization contant for the Probabilistic Hermite Physicist
        polynomial of order N
        """
        if (self.poly != HERMITEP):
            print >> self.sdout, "The method __GammaHermiteP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            return math.sqrt(np.pi) * 2.**N * factorial(N,exact=True)
        
    def __GammaHermiteF(self,N):
        """
        Returns the normalization contant for the Hermite function of order N
        """
        if (self.poly != HERMITEF):
            print >> self.sdout, "The method __GammaHermiteF cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            return np.sqrt(2.*np.pi)
    
    def __GammaHermiteP_Prob(self,N):
        """
        Returns the normalization contant for the Probabilistic Hermite 
        Probabilistic polynomial of order N
        """
        if (self.poly != HERMITEP_PROB):
            print >> self.sdout, "The method __GammaHermiteP_Prob cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            return factorial(N,exact=True)
    
    def __GammaORTHPOL(self,N):
        """
        Returns the normalization contant for the generic ORTHPOL polynomial of order N.
        The computation is performed using Gauss Quadrature.
        """
        if (self.poly != ORTHPOL):
            print >> self.sdout, "The method __GammaORTHPOL cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            (x,w,ierr) = self.__ORTHPOL_GQ(N+1)
            if ierr != 0:
                print >> self.sdout, "Error in ORTHPOL GaussQuadrature."
            P = self.__ORTHPOL(x,N)
            return np.dot(P.T**2.,w)
    
    def Gamma(self,N):
        """
        Gamma(): returns the normalization constant for the N-th polynomial
        
        Syntax:
            ``g = Gamma(N)``
        
        Input:
            * ``N`` = polynomial order
        
        Output:
            * ``g`` = normalization constant
        """
        if (self.poly == JACOBI):
            return self.__GammaJacobiP(N)
        elif (self.poly == HERMITEP):
            return self.__GammaHermiteP(N)
        elif (self.poly == HERMITEF):
            return self.__GammaHermiteF(N)
        elif (self.poly == HERMITEP_PROB):
            return self.__GammaHermiteP_Prob(N)
        elif (self.poly == LAGUERREP):
            return self.__GammaLaguerreP(N)
        elif (self.poly == LAGUERREF):
            return self.__GammaLaguerreF(N)
        elif (self.poly == ORTHPOL):
            return self.__GammaORTHPOL(N)
        else:
            print >> self.sdout, "[Spectral1D]: Gamma function not implemented yet for the selected polynomial %s" % self.poly
    
    def __GradJacobiVandermondeORTHPOL(self,r,N,k,norm):
        if (self.poly != JACOBI):
            raise ImportError( "The method __GradJacobiP cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly )
        else:
            if not ORTHPOL_SUPPORT:
                raise ImportError("The orthpol package is not installed on this machine.")
            # Unpack parameters
            alpha,beta = self.params
            
            (al,be,ierr) = orthpol.drecur(N+1,6,alpha,beta)
            dV = orthpol.vandermonde(r,N,al,be)
            
            if k > 0:
                for n in range(N+1):
                    if (n >= k):
                        dV[:,n] = gammaF(alpha+beta+N+1.+k)/(2.**k * gammaF(alpha+beta+N+1.)) * np.sqrt(self.__GammaJacobiP(N-k,alpha+k,beta+k)/self.__GammaJacobiP(N,alpha,beta)) * dV[:,n]
                    else:
                        dV[:,n] = 0.
            return dV
    
    def GradVandermonde1D(self,r,N,k,norm=True):
        """
        GradVandermonde1D(): Initialize the ``k``-th gradient of the modal basis ``N`` at ``r``
        
        Syntax:
            ``V = GradVandermonde1D(r,N,k,[norm])``
        
        Input:
            * ``r`` = (1d-array,float) set of ``M`` points on which to evaluate the polynomials
            * ``N`` = (int) maximum order in the vanermonde matrix
            * ``k`` = (int) derivative order
            * ``norm`` = (optional,boolean) True -> orthonormal polynomials, False -> non orthonormal polynomials
        
        Output:
            * ``V`` = (2d-array(``MxN``),float) Generalized Vandermonde matrix
        """
        
        if (self.poly == JACOBI) and ORTHPOL_SUPPORT:
            DVr = self.__GradJacobiVandermondeORTHPOL(r,N,k,norm)
        else:
            DVr = np.zeros((r.shape[0],N+1))
            for i in range(0,N+1):
                DVr[:,i] = self.GradEvaluate(r,i,k,norm)
        
        return DVr
        
    def AssemblyDerivativeMatrix(self, x, N, k):
        """
        AssemblyDerivativeMatrix(): Assemble the k-th derivative matrix using polynomials of order N.
        
        Syntax:
            ``Dk = AssemblyDerivativeMatrix(x,N,k)``
        
        Input:
            * x = (1d-array,float) Set of points on which to evaluate the polynomials
            * N = (int) maximum order in the vanermonde matrix
            * k = (int) derivative order
        
        Output:
            * Dk = Derivative matrix
        
        Description:
            This function performs ``D = linalg.solve(V.T, Vx.T)`` where ``V`` and ``Vx`` are a Generalized Vandermonde Matrix and its derivative respectively.
        
        Notes:
            For Chebyshev Polynomial, this function refers to the recursion form implemented in ``PolynomialDerivativeMatrix``
        """
        # Unpack parameters
        if (self.poly == JACOBI):
            alpha,beta = self.params
        
        if (self.poly == JACOBI) and ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
            return self.PolynomialDerivativeMatrix(x,k)
        else:
            V = self.GradVandermonde1D(x, N, 0)
            Vx = self.GradVandermonde1D(x, N ,1)
            D = LA.solve(V.T, Vx.T)
            D = D.T
            Dk = np.asarray(np.mat(D)**k)
            return Dk
            
    def PolyInterp(self, x, f, xi, order):
        """
        PolyInterp(): Interpolate function values ``f`` from points ``x`` to points ``xi`` using Forward and Backward Polynomial Transform
        
        Syntax:
            ``fi = PolyInterp(x, f, xi)``
        
        Input:
            * ``x`` = (1d-array,float) set of ``N`` original points where ``f`` is evaluated
            * ``f`` = (1d-array,float) set of ``N`` function values
            * ``xi`` = (1d-array,float) set of ``M`` points where the function is interpolated
            * ``order`` = (integer) order of polynomial interpolation
        
        Output:
            * ``fi`` = (1d-array,float) set of ``M`` function values
        
        Notes:
            
        """
        (fhat, residues, rank, s) = self.DiscretePolynomialTransform(x,f,order)
        return self.InverseDiscretePolynomialTransform(xi,fhat,order)
        
    def LegendreDerivativeCoefficients(self,fhat):
        """
        LegendreDerivativeCoefficients(): computes the Legendre coefficients of the derivative of a function
        
        Syntax:
            ``dfhat = LegendreDerivativeCoefficients(fhat)``
        
        Input:
            * ``fhat`` = (1d-array,float) list of Legendre coefficients of the original function
        
        Output:
            * ``dfhat`` = (1d-array,float) list of Legendre coefficients of the derivative of the original function
        
        Notes:
            Algorithm (4) from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,0.) and AlmostEqual(beta,0.) ):
                N = fhat.shape[0]-1
                dfhat = np.zeros((N+1))
                dfhat[N-1] = (2.*N - 1.) * fhat[N]
                for k in range(N-2, -1, -1):
                    dfhat[k] = (2.*k + 1.) * (fhat[k+1] + dfhat[k+2]/(2.*k + 5.) )
                return dfhat
    
    def ChebyshevDerivativeCoefficients(self,fhat):
        """
        ChebyshevDerivativeCoefficients(): computes the Chebyshev coefficients of the derivative of a function
        
        Syntax:
            ``dfhat = ChebyshevDerivativeCoefficients(fhat)``
        
        Input:
            * ``fhat`` = (1d-array,float) list of Chebyshev coefficients of the original function
        
        Output:
            * ``dfhat`` = (1d-array,float) list of Chebyshev coefficients of the derivative of the original function
        
        Notes:
            Algorithm (5) from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
                N = fhat.shape[0]-1
                dfhat = np.zeros((N+1))
                dfhat[N-1] = (2.*N) * fhat[N]
                for k in range(N-2, 0, -1):
                    dfhat[k] = 2. * (k + 1.) * fhat[k+1] + dfhat[k+2]
                dfhat[0] = fhat[1] + dfhat[2]/2.
                return dfhat
        
    def DiscretePolynomialTransform(self,r, f, N):
        """
        DiscretePolynomialTransform(): computes the Discrete Polynomial Transform of function values f
        
        Syntax:
            ``fhat = DiscretePolynomialTransform(r, f, N)``
        
        Input:
            * ``r`` = (1d-array,float) set of points on which to the polynomials are evaluated
            * ``f`` = (1d-array,float) function values
            * ``N`` = (int) maximum order in the generalized vanermonde matrix
        
        Output: one of the two following output is given, depending on the length of r
            * ``(fhat, residues, rank,s)`` = list of Polynomial coefficients and additional ouputs from function ``numpy.linalg.lstsq`` (if len(r) > N+1)
        
        Description:
            If the Chebyshev polynomials are chosen and ``r`` contains Chebyshev-Gauss-Lobatto points, the Fast Chebyshev Transform is used. Otherwise uses the Generalized Vandermonde Matrix in order to transform from physical space to transform space.
        
        .. seealso:: FastChebyshevTransform
        
        """
        # Unpack parameters
        if (self.poly == JACOBI):
            alpha,beta = self.params
        
        if (self.poly == JACOBI) and ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
            # Chebyshev case
            rr,w = self.__JacobiCGL(N)
            equal = True
            for i in range(0,N+1):
                equal = AlmostEqual(r[i],rr[i])
                if (not equal) :
                    break
            if equal:
                # Chebyshev-Gauss-Lobatto points. Use FCS.
                return self.FastChebyshevTransform(f)
        # Use the generalized vandermonde matrix
        V = self.GradVandermonde1D(r, N, 0)
        if ( V.shape[0] == V.shape[1] ):
            fhat = LA.solve(V, f)
            residues = np.zeros((0))
            rank = -1
            s = np.zeros((0))
        else:
            (fhat, residues, rank, s) = LA.lstsq(V, f)
        return (fhat, residues, rank, s)
        
    def InverseDiscretePolynomialTransform(self, r, fhat, N):
        """
        InverseDiscretePolynomialTransform(): computes the nodal values from the modal form fhat.
        
        Syntax:
            ``f = InverseDiscretePolynomialTransform(r, fhat, alpha, beta, N)``
        
        Input:
            * ``x`` = (1d-array,float) set of points on which to the polynomials are evaluated
            * ``fhat`` = (1d-array,float) list of Polynomial coefficients
            * ``N`` = (int) maximum order in the generalized vanermonde matrix
        
        Output:
            * ``f`` = (1d-array,float) function values
            
        Description:
            If the Chebyshev polynomials are chosen and r contains Chebyshev-Gauss-Lobatto points, the Inverse Fast Chebyshev Transform is used. Otherwise uses the Generalized Vandermonde Matrix in order to transform from transform space to physical space.
        
        .. seealso:: InverseFastChebyshevTransform
        
        """
        # Unpack parameters
        if (self.poly == JACOBI):
            alpha,beta = self.params
        
        if (self.poly == JACOBI) and ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
            # Chebyshev case
            rr,w = self.__JacobiCGL(N)
            equal = True
            for i in range(0,N+1):
                equal = AlmostEqual(r[i],rr[i])
                if (not equal) :
                    break
            if equal:
                # Chebyshev-Gauss-Lobatto points. Use FCS.
                return self.InverseFastChebyshevTransform(fhat)
        # Use the generalized vandermonde matrix
        V = self.GradVandermonde1D(r, N, 0)
        f = np.dot(V,fhat)
        return f
        
    def FastChebyshevTransform(self,f):
        """
        FastChebyshevTransform(): Returns the coefficients of the Fast Chebyshev Transform.
        
        Syntax:
            ``fhat = FastChebyshevTransform(f)``
        
        Input:
            * ``f`` = (1d-array,float) function values
        
        Output:
            * ``fhat`` = (1d-array,float) list of Polynomial coefficients
        
        .. warning:: It is assumed that the values f are computed at Chebyshev-Gauss-Lobatto points.
        
        .. note:: If f is odd, the vector is interpolated to even Chebyshev-Gauss-Lobatto points.
        .. note:: Modification of algorithm (29) from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
                N = f.shape[0]-1
                # Create Even function
                fbar = np.hstack([f[::-1], f[1:N]])
                # Transform
                fhat = FFT.ifft(fbar)
                fhat = np.hstack([fhat[0], 2*fhat[1:N], fhat[N]])
                return fhat
        
    def InverseFastChebyshevTransform(self,fhat):
        """
        InverseFastChebyshevTransform(): Returns the coefficients of the Inverse Fast Chebyshev Transform.
        
        Syntax:
            ``f = InverseFastChebyshevTransform(fhat)``
        
        Input:
            * ``fhat`` = (1d-array,float) list of Polynomial coefficients
        
        Output:
            * ``f`` = (1d-array,float) function values
        
        .. note:: If f is odd, the vector is padded with a zero value (highest freq.)
        .. note:: Modification of algorithm (29) from [1]_
        """
        if (self.poly != JACOBI):
            print >> self.sdout, "The method cannot be called with the actual type of polynomials. Actual type: '%s'" % self.poly
        else:
            # Unpack parameters
            alpha,beta = self.params
            if ( AlmostEqual(alpha,-0.5) and AlmostEqual(beta,-0.5) ):
                N = fhat.shape[0]
                # Sort values out for FFT
                fhat = np.hstack([fhat[0], np.hstack([fhat[1:N-1], fhat[N-1]*2, fhat[-2:0:-1] ])*0.5 ])
                f = FFT.fft(fhat)
                f = f[N-1::-1]
                f = np.real(f)
                return f
    
    def GramSchmidt(self, p, N, w):
        """
        GramSchmidt(): creates a Generalized Vandermonde Matrix of orthonormal polynomials with respect to the weights ``w``
        
        Syntax:
            ``V = GramSchmidt(p, N, w)``
        
        Input:
            * ``p`` = (1d-array,float) points at which to evaluate the new polynomials
            * ``N`` = (int) the maximum order of the polynomials
            * ``w`` = (1d-array,float) weights to be used for the orthogonoalization
        
        Output:
            * ``V`` = Generalized Vandermonde Matrix containing the new orthogonalized polynomials
        
        Description:
            Takes the points where the polynomials have to be evaluated and computes a Generalized Gram Schmidth procedure, where a weighted projection is used. If ``w==1`` then the usual inner product is used for the orthogonal projection.
        """
        # Evaluate Vandermonde matrix 
        V = np.vander(p,N+1)
        V  = V[:,::-1]
        
        # Evaluate Gram-Shmidt orthogonalization
        gs = np.zeros(N+1) # Vector of gamma values for the new polynomials
        for k in range(0,N+1):
            for j in range(0,N+1):
                for i in range(0,j):
                    # Use numerical quadrature to evaluate the projection
                    V[:,j] = V[:,j] - np.dot(V[:,j] * V[:,i], w) / np.sqrt(gs[i]) * V[:,i]
                # Compute the gamma value for the new polynomial
                gs[j] = np.dot(V[:,j]*V[:,j],w)
                # Normalize the vector if required
                V[:,j] = V[:,j]/np.sqrt(gs[j])
        
        return V
    
def AlmostEqual(a,b):
    """
    b = AlmostEqual(a,b)
    Test equality of two floating point numbers. Returns a boolean.
    """
    eps = np.finfo(np.float64).eps
    if ((a == 0) or (b == 0)):
        if (abs(a-b) <= 2*eps):
            return True
        else:
            return False
    else:
        if ( (abs(a-b) <= eps*abs(a)) and (abs(a-b) <= eps*abs(b)) ):
            return True
        else:
            return False

def TestOrthogonality( V, w):
    N = V.shape[1]
    orth = np.zeros((N,N))
    for i in range(0,N):
        for j in range(0,N):
            # Use numerical quadrature to compute the orthogonality constants
            orth[i,j] = np.dot( V[:,i]* V[:,j], w)
    return orth


def FirstPolynomialDerivativeMatrix(x):
    """
    PolynomialDerivativeMatrix(): Assemble the first Polynomial Derivative Matrix using matrix multiplication.

    Syntax:
        ``D = FirstPolynomialDerivativeMatrix(x)``

    Input:
        * ``x`` = (1d-array,float) set of points on which to evaluate the derivative matrix

    Output:
        * ``D`` = derivative matrix

    Notes:
        Algorithm (37) from [1]_
    """
    N = x.shape[0]
    w = BarycentricWeights(x)
    D = np.zeros((N,N))
    for i in range(0,N):
        for j in range(0,N):
            if (j != i):
                D[i,j] = w[j]/w[i] * 1./(x[i] - x[j])
                D[i,i] = D[i,i] - D[i,j]
    return D

def PolynomialDerivativeMatrix(x,k):
    """
    PolynomialDerivativeMatrix(): Assemble the Polynomial ``k``-th Derivative Matrix using the matrix recursion. This algorithm is generic for every types of polynomials.

    Syntax:
        ``D = PolynomialDerivativeMatrix(x,k)``

    Input:
        * ``x`` = (1d-array,float) set of points on which to evaluate the derivative matrix
        * ``k`` = derivative order

    Output:
        * ``D`` = ``k``-th derivative matrix

    Notes:
        Algorithm (38) taken from [1]_
    """
    N = x.shape[0]
    w = BarycentricWeights(x)
    D = np.zeros((N,N,k))
    D[:,:,0] = FirstPolynomialDerivativeMatrix(x)
    if ( k == 1 ): return D[:,:,k-1]
    for m in range(2,k+1):
        for i in range(0,N):
            for j in range(0,N):
                if ( j != i ):
                    D[i,j,m-1] = m/(x[i]-x[j]) * ( w[j]/w[i] * D[i,i,m-2] - D[i,j,m-2])
                    D[i,i,m-1] = D[i,i,m-1] - D[i,j,m-1]
    return D[:,:,k-1]

def BarycentricWeights(x):
    """
    BarycentricWeights(): Returns a 1-d array of weights for Lagrange Interpolation

    Syntax:
        ``w = BarycentricWeights(x)``

    Input:
        * ``x`` = (1d-array,float) set of points

    Output:
        * ``w`` = (1d-array,float) set of barycentric weights

    Notes:
        Algorithm (30) from [1]_
    """
    N = x.shape[0]
    w = np.zeros((N))
    for j in range(0,N):
        w[j] = 1.
    for j in range(1,N):
        for k in range(0,j):
            w[k] = w[k] * (x[k] - x[j])
            w[j] = w[j] * (x[j] - x[k])
    for j in range(0,N):
        w[j] = 1. / w[j]
    return w

def LagrangeInterpolationMatrix(x, w, xi):
    """
    LagrangeInterpolationMatrix(): constructs the Lagrange Interpolation Matrix from points ``x`` to points ``xi``

    Syntax:
        ``T = LagrangeInterpolationMatrix(x, w, xi)``

    Input:
        * ``x`` = (1d-array,float) set of ``N`` original points
        * ``w`` = (1d-array,float) set of ``N`` barycentric weights
        * ``xi`` = (1d-array,float) set of ``M`` interpolating points

    Output:
        * ``T`` = (2d-array(``MxN``),float) Lagrange Interpolation Matrix

    Notes:
        Algorithm (32) from [1]_
    """
    N = x.shape[0]
    M = xi.shape[0]
    T = np.zeros((M,N))
    for k in range(0,M):
        rowHasMatch = False
        for j in range(0,N):
            T[k,j] = 0.
            if AlmostEqual(xi[k],x[j]):
                rowHasMatch = True
                T[k,j] = 1.
        if (rowHasMatch == False):
            s = 0.
            for j in range(0,N):
                t = w[j] / (xi[k] - x[j])
                T[k,j] = t
                s = s + t
            for j in range(0,N):
                T[k,j] = T[k,j] / s
    return T

def LagrangeInterpolate(x, f, xi):
    """
    LagrangeInterpolate(): Interpolate function values ``f`` from points ``x`` to points ``xi`` using Lagrange weights

    Syntax:
        ``fi = LagrangeInterpolate(x, f, xi)``

    Input:
        * ``x`` = (1d-array,float) set of ``N`` original points where ``f`` is evaluated
        * ``f`` = (1d-array/2d-array,float) set of ``N`` function values (if K functions are passed, the values are stored in a NxK matrix)
        * ``xi`` = (1d-array,float) set of ``M`` points where the function is interpolated

    Output:
        * ``fi`` = (1d-array,float) set of ``M`` function values (if K functions are passed, the values are stored in a MxK matrix)

    Notes:
        Modification of Algorithm (33) from [1]_
    """
    # Obtain barycentric weights
    w = BarycentricWeights(x)
    # Generate the Interpolation matrix
    T = LagrangeInterpolationMatrix(x, w, xi)
    # Compute interpolated values
    fi = np.dot(T,f)
    return fi

def LinearShapeFunction(x,xm,xp,xi):
    """ Hat function used for linear interpolation
    
    :param array x: 1d original points
    :param float xm,xp: bounding points of the support of the shape function
    :param array xi: 1d interpolation points

    :returns array N: evaluation of the shape function on xi
    """
    N = np.zeros(len(xi))
    if x != xm: N += (xi - xm)/(x - xm) * ((xi >= xm)*(xi <= x)).astype(float)
    if x != xp: N += ((x - xi)/(xp - x) + 1.) * ((xi >= x)*(xi <= xp)).astype(float)
    return N

def SparseLinearShapeFunction(x,xm,xp,xi):
    """ Hat function used for linear interpolation. 
    Returns sparse indices for construction of scipy.sparse.coo_matrix.
    
    :param array x: 1d original points
    :param float xm,xp: bounding points of the support of the shape function
    :param array xi: 1d interpolation points

    :returns tuple (idxs,vals): List of indexes and evaluation of the shape function on xi
    """
    idxs = []
    vals = []
    if x != xm:
        bool_idxs = (xi >= xm)*(xi <= x)
        idxs.extend( np.where(bool_idxs)[0] )
        vals.extend( (xi[bool_idxs] - xm)/(x - xm) )
    if x != xp:
        bool_idxs = (xi >= x)*(xi <= xp)
        idxs.extend( np.where(bool_idxs)[0] )
        vals.extend( ((x - xi[bool_idxs])/(xp - x) + 1.) )
    return (idxs,vals)

def LinearInterpolationMatrix(x, xi):
    """
    LinearInterpolationMatrix(): constructs the Linear Interpolation Matrix from points ``x`` to points ``xi``

    Syntax:
        ``T = LagrangeInterpolationMatrix(x, xi)``

    Input:
        * ``x`` = (1d-array,float) set of ``N`` original points
        * ``xi`` = (1d-array,float) set of ``M`` interpolating points

    Output:
        * ``T`` = (2d-array(``MxN``),float) Linear Interpolation Matrix

    """
    
    M = np.zeros((len(xi),len(x)))
    
    M[:,0] = LinearShapeFunction(x[0],x[0],x[1],xi)
    M[:,-1] = LinearShapeFunction(x[-1],x[-2],x[-1],xi)
    for i in range(1,len(x)-1):
        M[:,i] = LinearShapeFunction(x[i],x[i-1],x[i+1],xi)

    return M

def SparseLinearInterpolationMatrix(x,xi):
    """
    LinearInterpolationMatrix(): constructs the Linear Interpolation Matrix from points ``x`` to points ``xi``.
    Returns a scipy.sparse.coo_matrix

    Syntax:
        ``T = LagrangeInterpolationMatrix(x, xi)``

    Input:
        * ``x`` = (1d-array,float) set of ``N`` original points
        * ``xi`` = (1d-array,float) set of ``M`` interpolating points

    Output:
        * ``T`` = (scipy.sparse.coo_matrix(``MxN``),float) Linear Interpolation Matrix

    """
    
    rows = []
    cols = []
    vals = []
    
    (ii,vv) = SparseLinearShapeFunction(x[0],x[0],x[1],xi)
    rows.extend( ii )
    cols.extend( [0] * len(ii) )
    vals.extend( vv )

    (ii,vv) = SparseLinearShapeFunction(x[-1],x[-2],x[-1],xi)
    rows.extend( ii )
    cols.extend( [len(x)-1] * len(ii) )
    vals.extend( vv )

    for j in range(1,len(x)-1):
        (ii,vv) = SparseLinearShapeFunction(x[j],x[j-1],x[j+1],xi)
        rows.extend( ii )
        cols.extend( [j] * len(ii) )
        vals.extend( vv )

    M = scsp.coo_matrix( (np.asarray(vals), (np.asarray(rows),np.asarray(cols))), shape=( len(xi), len(x) ) )
    return M

def gqu(N,norm=True):
    """
    GQU(): function for generating 1D Gaussian quadrature rules for unweighted integral over [-1,1] (Gauss-Legendre)

    Note:: Max ``N'' is 25

    Syntax:
        (n,w) = GQU(l)
    Input:
        l = level of accuracy of the quadrature rule
    Output:
        n = nodes
        w = weights
    """
    (x,w) = SG.GQU(N)
    if (N % 2 == 0):
        x = np.asarray(x)
        x = np.hstack([1-x[::-1],x])
        w = np.asarray(w)
        w = np.hstack([w[::-1],w])
    else:
        x = np.asarray(x)
        x = np.hstack([1-x[1:][::-1],x])
        w = np.asarray(w)
        w = np.hstack([w[1:][::-1],w])
    
    x = x*2. - 1.
    if not norm: w *= 2.
    return (x,w)

def gqn(N):
    """
    GQN(): function for generating 1D Gaussian quadrature for integral with Gaussian weight (Gauss-Hermite)

    Note:: Max ``N'' is 25

    Syntax:
        (n,w) = GQU(l)
    Input:
        l = level of accuracy of the quadrature rule
    Output:
        n = nodes
        w = weights
    """
    (x,w) = SG.GQN(N)
    if (N % 2 == 0):
        x = np.asarray(x)
        x = np.hstack([-x[::-1],x])
        w = np.asarray(w)
        w = np.hstack([w[::-1],w])
    else:
        x = np.asarray(x)
        x = np.hstack([-x[1:][::-1],x])
        w = np.asarray(w)
        w = np.hstack([w[1:][::-1],w])
    return (x,w)

def kpu(N,norm=True):
    """
    KPU(): function for generating 1D Nested rule for unweighted integral over [-1,1]

    Note:: Max ``N'' is 25

    Syntax:
        (n,w) = GQU(l)
    Input:
        l = level of accuracy of the quadrature rule
    Output:
        n = nodes
        w = weights
    """
    (x,w) = SG.KPU(N)
    x = np.asarray(x)
    x = np.hstack([1-x[1:][::-1],x])
    x = x*2. - 1.
    w = np.asarray(w)
    w = np.hstack([w[1:][::-1],w])
    if not norm: w *= 2.
    return (x,w)

def kpn(N):
    """
    KPN(): function for generating 1D Nested rule for integral with Gaussian weight

    Note:: Max ``N'' is 25

    Syntax:
        (n,w) = GQU(l)
    Input:
        l = level of accuracy of the quadrature rule
    Output:
        n = nodes
        w = weights
    """
    (x,w) = SG.KPN(N)
    x = np.asarray(x)
    x = np.hstack([-x[1:][::-1],x])
    w = np.asarray(w)
    w = np.hstack([w[1:][::-1],w])
    return (x,w)

def cc(N,norm=True):
    """
    cc(): function for generating 1D Nested Clenshaw-Curtis [-1,1]

    Syntax:
        (n,w) = cc(N)
    Input:
        N = level of accuracy of the quadrature rule
    Output:
        n = nodes
        w = weights
    """
    (x,w) = SG.CC(N)
    x = np.hstack([-x[1:][::-1],x])
    w = np.hstack([w[1:][::-1],w])
    if norm: w /= np.sum(w)
    return (x,w)

def fej(N,norm=True):
    """
    fej(): function for generating 1D Nested Fejer's rule [-1,1]

    Syntax:
        (n,w) = fej(N)
    Input:
        N = level of accuracy of the quadrature rule
    Output:
        n = nodes
        w = weights
    """
    (x,w) = SG.FEJ(N)
    x = np.hstack([-x[1:][::-1],x])
    w = np.hstack([w[1:][::-1],w])
    if norm: w /= np.sum(w)
    return (x,w)

QUADS = {GQU: gqu,
         GQN: gqn,
         KPU: kpu,
         KPN: kpn,
         CC: cc,
         FEJ: fej}
