================
Spectral Toolbox
================

The SpectralToolbox is a collection of tools useful for spectral approximation methods in one or more dimensions.
It include the construction of traditional orthogonal polynomials. Additionally one can construct orthogonal polynomials with respect to a selected measure.

Description
===========

Implementation of Spectral Methods in N dimension.

Available polynomials:
    * Jacobi
    * Hermite Physicist
    * Hermite Function
    * Hermite Probabilistic
    * Laguerre Polynomial
    * Laguerre Function
    * ORTHPOL package (generation of recursion coefficients using [1]_)

Available quadrature rules (related to selected polynomials):
    * Gauss
    * Gauss-Lobatto
    * Gauss-Radau

Available quadrature rules (without polynomial selection):
    * Kronrod-Patterson on the real line
    * Kronrod-Patterson uniform
    * Clenshaw-Curtis
    * Fejer's

Installation
============

For everything to go smooth, I suggest that you first install some dependencies separately: `numpy <https://pypi.python.org/pypi/numpy>`_, `scipy <https://pypi.python.org/pypi/scipy>`_, `matplotlib <https://pypi.python.org/pypi/matplotlib>`_ can be installed by:

    $ pip install numpy scipy matplotlib

If you want to accelerate some of the functionalities and work with orthogonal polynomials with respect to arbitrary measures, you should intall the `orthpol <https://pypi.python.org/pypi/orthpol>`_ package. This dependency is optional. The installation might require you to tweak some flags for the compiler (with gcc nothing should be needed).

   $ pip install orthpol

Finally you can install the toolbox by:

   $ pip install SpectralToolbox


References
==========
.. [1] W. Gautschi, "Algorithm 726: ORTHPOL -- a package of routines for generating orthogonal polynomials and Gauss-type quadrature rules". ACM Trans. Math. Softw., vol. 20, issue 1, pp. 21-62, 1994
