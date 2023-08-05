from solver import Solver
import numpy as np
import sys
import cv2
from hindemith.operations.zip_with import zip_with, ZipWith
from hindemith.types.hmarray import hmarray, EltWiseArrayOp, empty, zeros, indices
from hindemith.operations.map import sqrt, SpecializedMap, square
from hindemith.utils import symbols
from hindemith.operations.structured_grid import structured_grid
from hindemith.operations.reduce import sum
from hindemith.operations.interp import interp_linear
from hindemith.meta.core import meta
# import logging
# logging.basicConfig(level=20)
from ctree.util import Timer
from box import get_boxes


EltWiseArrayOp.backend = 'ocl'
ZipWith.backend = 'ocl'
SpecializedMap.backend = 'ocl'

num_warps = 2
n_inner = 10
n_outer = 10
median_filtering = 5
# theta = .3
theta = .25
# tau = .25
tau = .25
# l = .15  # lambda
l = .15  # lambda
# epsilon = 0.01
epsilon = 0.03
n = .5

symbol_table = {
    'num_warps': num_warps,
    'theta': theta,
    'tau': tau,
    'l': l,
    'epsilon': epsilon,
    'n': n
}


@symbols(symbol_table)
def th(rho_elt, gradient_elt, delta_elt, u_elt):
    thresh = float(l) * float(theta) * gradient_elt
    if rho_elt < -thresh:
        return float(l) * float(theta) * delta_elt + u_elt
    elif rho_elt > thresh:
        return float(-l) * float(theta) * delta_elt + u_elt
    elif gradient_elt > 1e-10:
        return -rho_elt / gradient_elt * delta_elt + u_elt
    else:
        return 0.0


spec_th = zip_with(th)


@meta
def update_u(u1, u2, rho_c, gradient, I1wx, I1wy, div_p1, div_p2):
    rho = rho_c + I1wx * u1 + I1wy * u2
    v1 = spec_th(rho, gradient, I1wx, u1)
    v2 = spec_th(rho, gradient, I1wy, u2)
    u1_new = v1 + div_p1 * theta
    u2_new = v2 + div_p2 * theta
    err = square(u1_new - u1) + square(u2_new - u2)
    return u1_new, u2_new, err


def centered_gradient(m):
    return np.gradient(m)


@structured_grid(border='zero')
def dx(src, output):
    for y, x in output:
        output[y, x] = src[y, x + 1] - src[y, x]


@structured_grid(border='zero')
def dy(src, output):
    for y, x in output:
        output[y, x] = src[y + 1, x] - src[y, x]


# @meta
def forward_gradient(m):
    return dx(m), dy(m)


@structured_grid(border='zero')
def div(v1, v2, output):
    for y, x in output:
        output[y, x] = v1[y, x] + v2[y, x] - v1[y, x - 1] - v2[y - 1, x]


def divergence(v1, v2):
    """Wrapped divergence for profiling"""
    return div(v1, v2)


taut = tau / theta
one = 1.0
# FIXME: Resolve these naming issues


@meta
def update_dual_variables(p11, p12, p21, p22, u1x, u1y, u2x, u2y):
    ng1 = sqrt(square(u1x) + square(u1y)) * taut + one
    ng2 = sqrt(square(u2x) + square(u2y)) * taut + one
    p11 = (p11 + u1x * taut) / ng1
    p12 = (p12 + u1y * taut) / ng1
    p21 = (p21 + u2x * taut) / ng2
    p22 = (p22 + u2y * taut) / ng2
    return p11, p12, p21, p22


@meta
def calc_grad_rho_c(i1wx, i1wy, i1w, u1, u2, i0):
    grad = i1wx * i1wx + i1wy * i1wy
    rho_c = i1w - i1wx * u1 - i1wy * u2 - i0
    return grad, rho_c


def cl_build_flow_map(xs, ys, u1, u2):
    _x = xs + u1
    _y = ys + u2
    return _x, _y


def warp(i1, i1x, i1y, _f1, _f2):
    i1w = interp_linear(i1, _f1, _f2)
    i1wx = interp_linear(i1x, _f1, _f2)
    i1wy = interp_linear(i1y, _f1, _f2)
    return i1w, i1wx, i1wy


class TVL1(Solver):
    def solve(self, i0, i1, u1, u2):
        scaled_epsilon = epsilon * epsilon * i0.size
        p11 = zeros(i1.shape, np.float32)
        p12 = zeros(i1.shape, np.float32)
        p21 = zeros(i1.shape, np.float32)
        p22 = zeros(i1.shape, np.float32)
        i1x, i1y = forward_gradient(i1)
        ys, xs = indices(u1.shape)
        # grad, rho_c = empty(i1.shape, np.float32), empty(i1.shape, np.float32)
        for w in range(num_warps):
            _f1, _f2 = cl_build_flow_map(xs, ys, u1, u2)
            # with Timer() as t:
            i1w, i1wx, i1wy = warp(i1, i1x, i1y, _f1, _f2)
            # print("warp", t.interval)
            grad, rho_c = calc_grad_rho_c(i1wx, i1wy, i1w, u1, u2, i0)
            n0 = 0
            error = sys.maxint
            while n0 < n_outer * n_inner and error > scaled_epsilon:
                # print("----------------")
                # with Timer() as t:
                div_p1, div_p2 = divergence(p11, p12), divergence(p21, p22)
                # print("divp1, divp2", t.interval)
                # with Timer() as t:
                u1, u2, err = update_u(u1, u2, rho_c, grad, i1wx, i1wy, div_p1,
                                       div_p2)
                # print("update u", t.interval)
                # with Timer() as t:
                error = sum(err)
                # print("error", t.interval)
                # with Timer() as t:
                u1x, u1y = forward_gradient(u1)
                u2x, u2y = forward_gradient(u2)
                # print("forward_grad", t.interval)
                # with Timer() as t:
                p11, p12, p21, p22 = update_dual_variables(
                    p11, p12, p21, p22, u1x, u1y, u2x, u2y)
                # print("update dual", t.interval)
                # print("----------------")
                n0 += 1
        return u1, u2


import os
file_path = os.path.dirname(os.path.realpath(__file__))

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", action='store_true', help="profile execution time")
    args = parser.parse_args()
    frame0 = cv2.imread('images/frame0.png')
    frame1 = cv2.imread('images/frame1.png')
    im0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
    im1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    tvl1 = TVL1(2, .5)
    # jit warmup
    for _ in range(1):
        tvl1(im0, im1)
    if args.profile:
        import cProfile
        cProfile.runctx('tvl1(im0, im1)', None, locals())
    else:
        with Timer() as t:
            u = tvl1(im0, im1)
        print("Specialized time: {}s".format(t.interval))
        mag, ang = cv2.cartToPolar(u[0], u[1])
        mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        ang = ang*180/np.pi/2
        hsv = np.zeros_like(frame1)
        hsv[..., 1] = 255
        hsv[..., 0] = ang
        hsv[..., 2] = mag
        flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        # cv2.imwrite('flow.jpg', flow)
        cv2.imshow('flow', flow)
        cv2.waitKey(0) & 0xff
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
