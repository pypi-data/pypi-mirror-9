from hindemith.types.hmarray import hmarray, zeros, indices
import numpy as np
import cv2
from hindemith.operations.interp import interp_linear
from hindemith.operations.reduce import sum
from hindemith.meta.core import meta
from hindemith.operations.map import square
from solver import Solver
from hindemith.utils import symbols

from stencil_code.stencil_kernel import Stencil
from ctree.util import Timer
import matplotlib.pyplot as plt
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
        [(1, 0)], [(-1, 0)]]

    def kernel(self, a, out_grid):
        for x in self.interior_points(out_grid):
            out_grid[x] = 0.0
            for y in self.neighbors(x, 0):
                out_grid[x] += .5 * a[y]
            for y in self.neighbors(x, 1):
                out_grid[x] -= .5 * a[y]


class Dy(Stencil):
    neighborhoods = [
        [(0, 1)], [(0, -1)]]

    def kernel(self, a, out_grid):
        for x in self.interior_points(out_grid):
            out_grid[x] = 0.0
            for y in self.neighbors(x, 0):
                out_grid[x] += .5 * a[y]
            for y in self.neighbors(x, 1):
                out_grid[x] -= .5 * a[y]

dx, dy = Dx(), Dy()

jacobi = Jacobi()

w = 1.9
w_inv = 1 - w


alpha = 15.0
alpha2 = alpha ** 2


# @meta
def gradient(im1):
    Ix = dx(im1)
    Iy = dy(im1)
    return Ix, Iy


def warp(im1, i1x, i1y, u, v):
    ys, xs = indices(u.shape)
    _x = xs + u
    _y = ys + v
    i1w = interp_linear(im1, _x, _y)
    i1wx = interp_linear(i1x, _x, _y)
    i1wy = interp_linear(i1y, _x, _y)
    return i1w, i1wy, i1wx


@meta
def get_a_d(i1wx, u, i1wy, v, im0, i1w):
    dif = im0 - i1w + i1wx * u + i1wy * v
    Au = dif * i1wx
    Av = dif * i1wy
    Du = i1wx * i1wx + alpha2
    Dv = i1wy * i1wy + alpha2
    D = i1wy * i1wx
    return Au, Av, Du, Dv, D


@meta
def compute_bar(u, v):
    return jacobi(u), jacobi(v)


@meta
def update_u(u, Au, D, v, ubar, Du):
    u_new = u * w_inv + (Au - D * v + ubar * alpha) * w / Du
    u_err = square(u_new - u)
    return u_new, u_err


@meta
def update_v(v, Av, D, u, vbar, Dv):
    v_new = v * w_inv + (Av - D * u + vbar * alpha) * w / Dv
    v_err = square(v_new - v)
    return v_new, v_err


# @meta
def update(u, v, Au, D, Du, Av, Dv):
    ubar, vbar = jacobi(u), jacobi(v)
    u_old = u
    v_old = v
    u, u_err = update_u(u, Au, D, v, ubar, Du)
    v, v_err = update_v(v, Av, D, u, vbar, Dv)
    err = u_err + v_err
    return u, v, err


class HS_Jacobi(Solver):
    def solve(self, im0, im1, u, v):
        Ix, Iy = gradient(im1)
        epsilon = (0.01 ** 2) * np.prod(u.shape)
        for n in range(2):
            i1w, i1wx, i1wy = warp(im1, Ix, Iy, u, v)
            Au, Av, Du, Dv, D = get_a_d(i1wx, u, i1wy, v, im0, i1w)

            for _ in range(100):
                u, v, err = update(u, v, Au, D, Du, Av, Dv)
                if sum(err) < epsilon:
                    break
        return u, v
