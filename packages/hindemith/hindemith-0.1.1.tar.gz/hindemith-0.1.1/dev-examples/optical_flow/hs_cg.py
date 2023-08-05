import numpy as np
# import logging
# logging.basicConfig(level=20)

from hindemith.operations.reduce import sum
from hindemith.meta.core import meta
from hindemith.operations.map import square, copy
from solver import Solver

from stencil_code.stencil_kernel import Stencil


class Jacobi(Stencil):
    neighborhoods = [[(0, 0)],
                     [(-1, 0), (1, 0), (0, -1), (0, 1)]]

    def kernel(self, in_grid, out_grid):
        for x in self.interior_points(out_grid):
            out_grid[x] = 0.0
            for y in self.neighbors(x, 0):
                out_grid[x] += .01 * in_grid[y]
            for y in self.neighbors(x, 1):
                out_grid[x] -= .0025 * in_grid[y]


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


@meta
def update(u, v, Ix, Iy, It, denom):
    ubar = jacobi(u)
    vbar = jacobi(v)
    t = (Ix * ubar + Iy * vbar + It) / denom
    u_new = ubar - Ix * t
    v_new = vbar - Iy * t
    err = square(u_new - u) + square(v_new - v)
    return u_new, v_new, err

alpha = 15.0
alpha2 = alpha ** 2


@meta
def compute_denom(Ix, Iy):
    return square(Ix) + square(Iy) + alpha2


@meta
def gradient(im0, im1):
    It = im1 - im0
    Ix = dx(im1)
    Iy = dy(im1)
    return Ix, Iy, It


class HS_Jacobi(Solver):
    def solve(self, im0, im1, u, v):
        Ix, Iy, It = gradient(im0, im1)
        epsilon = 1e-10

        Ix2 = Ix * Ix 
        IxIy = Ix * Iy
        Iy2 = Iy * Iy

        b0 = Ix * It
        b1 = Iy * It
        b0 = 0.0 - b0
        b1 = 0.0 - b1
        ubar = jacobi(u)
        vbar = jacobi(v)
        r0 = b0 - (ubar + Ix2*u + IxIy * v)
        r1 = b1 - (vbar + Iy2*v + IxIy * u)
        p0 = b0 - (ubar + Ix2*u + IxIy * v)
        p1 = b1 - (vbar + Iy2*v + IxIy * u)
        rsold = sum(r0 * r0 + r1 * r1)
        print(rsold)
        for i in range(100):
          Ap0 = (jacobi(p0) + Ix2 * p0 + IxIy * p1)
          Ap1 = (jacobi(p1) + Iy2 * p1 + IxIy * p0)
          alpha = rsold / sum(p0 * Ap0 + p1 * Ap1)
          u = u + alpha * p0
          v = v + alpha * p1
          r0 = r0 - alpha * Ap0
          r1 = r1 - alpha * Ap1
          rsnew = sum(r0 * r0 + r1 * r1)
          print(rsnew)
          if rsnew < epsilon:
            break
          beta = rsnew / rsold
          p0 = r0 + beta * p0
          p1 = r1 + beta * p1
          rsold = rsnew

        return u, v

if __name__ == '__main__':
    import cv2
    frame0 = cv2.imread('images/frame0.png')
    frame1 = cv2.imread('images/frame1.png')
    frame0 = cv2.resize(frame0, (384, 288))
    frame1 = cv2.resize(frame1, (384, 288))
    im0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
    im1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    hs_jacobi = HS_Jacobi(1, .5)

    from ctree.util import Timer
    hs_jacobi(im0, im1)
    with Timer() as t:
        u = hs_jacobi(im0, im1)
    print(t.interval)
    mag, ang = cv2.cartToPolar(u[0], u[1])
    mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    ang = ang*180/np.pi/2
    hsv = np.zeros_like(frame1)
    hsv[..., 1] = 255
    hsv[..., 0] = ang
    hsv[..., 2] = mag
    flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    cv2.imshow('flow', flow)
    cv2.waitKey()
