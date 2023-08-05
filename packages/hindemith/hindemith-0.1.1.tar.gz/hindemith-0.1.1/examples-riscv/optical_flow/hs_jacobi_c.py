import numpy as np
# import logging
# logging.basicConfig(level=20)

# from hindemith.operations.reduce import sum
from hindemith.meta.core import meta
from hindemith.types.hmarray import hmarray
from hindemith.operations.map import square, copy
from r5solver import Solver

from stencil_code.stencil_kernel import Stencil


class Jacobi(Stencil):
    neighborhoods = [[(0, -1), (0, 1), (-1, 0), (1, 0)],
                     [(-1, -1), (-1, 1), (1, -1), (1, 1)]]

    def kernel(self, in_grid, out_grid):
        for x in self.interior_points(out_grid):
            out_grid[x] = 0.0
            for y in self.neighbors(x, 0):
                out_grid[x] += .166666667 * in_grid[y]
            for y in self.neighbors(x, 1):
                out_grid[x] += .083333333 * in_grid[y]


class Dx(Stencil):
    neighborhoods = [
        [(1, 0), (1, 1)],
        [(0, 0), (0, 1)]]

    def kernel(self, a, b, out_grid):
        for x in self.interior_points(out_grid):
            out_grid[x] = 0.0
            for y in self.neighbors(x, 0):
                out_grid[x] += .25 * (a[y] + b[y])
            for y in self.neighbors(x, 1):
                out_grid[x] -= .25 * (a[y] + b[y])


class Dy(Stencil):
    neighborhoods = [
        [(0, 1), (1, 1)],
        [(0, 0), (1, 0)]]

    def kernel(self, a, b, out_grid):
        for x in self.interior_points(out_grid):
            out_grid[x] = 0.0
            for y in self.neighbors(x, 0):
                out_grid[x] += .25 * (a[y] + b[y])
            for y in self.neighbors(x, 1):
                out_grid[x] -= .25 * (a[y] + b[y])


class Dt(Stencil):
    neighborhoods = [
        [(0, 0), (1, 0), (0, 1), (1, 1)]]

    def kernel(self, a, b, out_grid):
        for x in self.interior_points(out_grid):
            for y in self.neighbors(x, 0):
                out_grid[x] += .25 * (b[y] - a[y])

dx, dy, dt = Dx(backend='c'), Dy(backend='c'), Dt(backend='c')

jacobi = Jacobi(backend='c')


@meta
def update(u, v, Ix, Iy, It, denom):
    ubar = jacobi(u)
    vbar = jacobi(v)
    t = (Ix * ubar + Iy * vbar + It) / denom
    u_new = ubar - Ix * t
    v_new = vbar - Iy * t
    return u_new, v_new

alpha = 15.0
alpha2 = alpha ** 2


@meta
def compute_denom(Ix, Iy):
    return square(Ix) + square(Iy) + alpha2


@meta
def gradient_and_denom(im0, im1):
    Ix = dx(im0, im1)
    Iy = dy(im0, im1)
    It = im1 - im0
    denom = square(Ix) + square(Iy) + alpha2
    return Ix, Iy, It, denom


@meta
def compute_err(u, u_new, v, v_new):
    return square(u - u_new) + square(v - v_new)


class HS_Jacobi(Solver):
    def solve(self, im0, im1, u, v):
        Ix, Iy, It, denom = gradient_and_denom(im0, im1)
        epsilon = (0.02 ** 2) * np.prod(u.shape)

        for _ in range(100):
            u_new, v_new = update(u, v, Ix, Iy, It, denom)
            err = compute_err(u, u_new, v, v_new)
            if np.sum(err) < epsilon:
                break
            u, v = u_new, v_new
        return u, v
