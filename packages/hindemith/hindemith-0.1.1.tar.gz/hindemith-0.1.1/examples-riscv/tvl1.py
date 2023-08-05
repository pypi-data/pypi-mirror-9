import numpy as np
import sys
import cv2
from hindemith.operations.zip_with import zip_with, ZipWith
from hindemith.types.hmarray import hmarray, EltWiseArrayOp, empty, zeros
from hindemith.operations.map import sqrt, SpecializedMap, square
from hindemith.utils import symbols
from hindemith.operations.structured_grid import structured_grid
from hindemith.operations.reduce import sum
from hindemith.operations.interp import interp_linear
from hindemith.meta.core import meta  # , while_loop
# import logging
# logging.basicConfig(level=20)
from ctree.util import Timer
from box import get_boxes
from detect import run


EltWiseArrayOp.backend = 'ocl'
ZipWith.backend = 'ocl'
SpecializedMap.backend = 'ocl'


num_warps = 5
n_scales = 5
n_inner = 10
n_outer = 10
median_filtering = 5
theta = .3
tau = .25
l = .15  # lambda
epsilon = 0.01
n = .5

symbol_table = {
    'num_warps': num_warps,
    'n_scales': n_scales,
    'theta': theta,
    'tau': tau,
    'l': l,
    'epsilon': epsilon,
    'n': n
}


@symbols(symbol_table)
def th(rho_elt, gradient_elt, delta_elt, u_elt):
    thresh = float(l * theta * gradient_elt)
    if rho_elt < -thresh:
        return float(l * theta * delta_elt) + u_elt
    elif rho_elt > thresh:
        return float(-l * theta * delta_elt) + u_elt
    elif gradient_elt > 1e-10:
        return float(-rho_elt / gradient_elt * delta_elt) + u_elt
    else:
        return 0


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


@structured_grid(border='constant', cval=0)
def divergence(v1, v2, output):
    for y, x in output:
        output[y, x] = v1[y, x] + v2[y, x] - v1[y, x - 1] - v2[y - 1, x]


@meta
def forward_gradient(m):
    _dx = dx(m)
    _dy = dy(m)
    return _dx, _dy


def pyr_down(m, n_scales, n):
    pyr = [hmarray(m)]
    for _ in range(n_scales - 1):
        scaled = tuple(s * n for s in m.shape)
        y, x = np.indices(scaled).astype(np.float32)
        curr = pyr[-1]
        y = y * (curr.shape[0] / scaled[0])
        x = x * (curr.shape[1] / scaled[1])
        pyr.append(interp_linear(curr, hmarray(x), hmarray(y)))
    return pyr


def pyr_up(m, shape):
    y, x = np.indices(shape).astype(np.float32)
    y = hmarray(y) * (m.shape[0] / shape[0])
    x = hmarray(x) * (m.shape[1] / shape[1])
    return interp_linear(m, hmarray(x), hmarray(y))


def build_flow_map(idxs, u1, u2):
    _x = idxs[1].__add__(u1)
    _y = idxs[0].__add__(u2)
    return _x, _y


def cl_build_flow_map(xs, ys, u1, u2):
    _x = xs + u1
    _y = ys + u2
    return _x, _y


taut = tau / theta
one = 1.0
# FIXME: Resolve these naming issues


@meta
def update_dual_variables(p11, p12, p21, p22, u1, u2):
    u1x = dx(u1)
    u1y = dy(u1)
    u2x = dx(u2)
    u2y = dy(u2)
    ng1 = sqrt(square(u1x) + square(u1y)) * taut + one
    ng2 = sqrt(square(u2x) + square(u2y)) * taut + one
    p11 = (p11 + u1x * taut) / ng1
    p12 = (p12 + u1y * taut) / ng1
    p21 = (p21 + u2x * taut) / ng2
    p22 = (p22 + u2y * taut) / ng2
    return p11, p12, p21, p22


@meta
def calc_grad_rho_c(i1wx, i1wy, i1w, u1, u2, i0, grad, rho_c):
    grad = i1wx * i1wx + i1wy * i1wy
    rho_c = i1w - i1wx * u1 - i1wy * u2 - i0
    return grad, rho_c


def do_while_loop(n0, error, scaled_epsilon, u1, u2, p11, p12, p21, p22, i1wx,
                  i1wy, rho_c, grad):
    while n0 < n_outer * n_inner and error > scaled_epsilon:
        div_p1, div_p2 = divergence(p11, p12), divergence(p21, p22)
        u1, u2, err = update_u(u1, u2, rho_c, grad, i1wx, i1wy, div_p1,
                               div_p2)
        error = sum(err)
        p11, p12, p21, p22 = update_dual_variables(
            p11, p12, p21, p22, u1, u2)
        del div_p1
        del div_p2
        n0 += 1
    return u1, u2, p11, p12, p21, p22


def compute_flow(i0, i1, u1, u2):
    scaled_epsilon = epsilon * epsilon * i0.size
    p11 = zeros(i1.shape, np.float32)
    p12 = zeros(i1.shape, np.float32)
    p21 = zeros(i1.shape, np.float32)
    p22 = zeros(i1.shape, np.float32)
    i1x, i1y = forward_gradient(i1)
    indices = np.indices(u1.shape).astype(np.float32)
    xs = hmarray(indices[1])
    ys = hmarray(indices[0])
    grad, rho_c = empty(i1.shape, np.float32), empty(i1.shape, np.float32)
    for w in range(num_warps):
        _f1, _f2 = cl_build_flow_map(xs, ys, u1, u2)
        i1w = interp_linear(i1, _f1, _f2)
        i1wx = interp_linear(i1x, _f1, _f2)
        i1wy = interp_linear(i1y, _f1, _f2)
        grad, rho_c = calc_grad_rho_c(i1wx, i1wy, i1w, u1, u2, i0, grad, rho_c)
        u1, u2, p11, p12, p21, p22 = do_while_loop(
            0, sys.maxint, scaled_epsilon, u1, u2, p11, p12, p21, p22, i1wx,
            i1wy, rho_c, grad)
        del i1w
        del i1wx
        del i1wy
    return u1, u2


def tvl1(im0, im1):
    im0 = cv2.GaussianBlur(im0, (11, 11), 1.5)
    im1 = cv2.GaussianBlur(im1, (11, 11), 1.5)
    im0 = im0.astype(np.float32)
    im1 = im1.astype(np.float32)
    im0_pyr = pyr_down(im0, n_scales, n)
    im1_pyr = pyr_down(im1, n_scales, n)
    u1 = hmarray(np.zeros(im0_pyr[-1].shape, dtype=np.float32))
    u2 = hmarray(np.zeros(im0_pyr[-1].shape, dtype=np.float32))
    for s in reversed(range(n_scales)):
        u1, u2 = compute_flow(im0_pyr[s], im1_pyr[s], u1, u2)
        if s > 0:
            u1 = pyr_up(u1, im0_pyr[s - 1].shape) * (1.0 / n)
            u2 = pyr_up(u2, im0_pyr[s - 1].shape) * (1.0 / n)
    u1.copy_to_host_if_dirty()
    u2.copy_to_host_if_dirty()
    return u1, u2

import os

import glob

file_path = os.path.dirname(os.path.realpath(__file__))


def main(*args):
    if args[0] and args[0][0] == "--video":
        frame0 = None
        for i, filename in enumerate(sorted(glob.glob('image*.png'))):
            if frame0 is None:
                frame0 = cv2.imread(filename)
                hsv = np.zeros_like(frame0)
                frame0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
                continue
            frame1 = cv2.imread(filename)

            gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            u = tvl1(frame0, gray)
            mag, ang = cv2.cartToPolar(u[0], u[1])
            mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
            ang = ang*180/np.pi/2
            hsv[..., 1] = 255
            hsv[..., 0] = ang
            hsv[..., 2] = mag
            left = np.copy(mag)
            left[np.where(ang <= 60)] = 0
            left[np.where(ang >= 90)] = 0
            windows1 = get_boxes(left, frame1)

            right = np.copy(mag)
            right[np.where(ang >= 30)] = 0
            windows2 = get_boxes(right, frame1)
            run([(filename, np.array(windows1 + windows2))], frame1)
            cv2.imwrite('{0:05d}.jpg'.format(i), frame1)
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
            frame0 = gray
    else:
        frame0 = cv2.imread(file_path + '/frame0.png')
        frame1 = cv2.imread(file_path + '/frame1.png')
        im0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
        im1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        # u = tvl1(im0, im1)
        with Timer() as t:
            u = tvl1(im0, im1)
        print("Specialized time: {}".format(t.interval))
        mag, ang = cv2.cartToPolar(u[0], u[1])
        mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        ang = ang*180/np.pi/2
        hsv = np.zeros_like(frame1)
        hsv[..., 1] = 255
        hsv[..., 0] = ang
        hsv[..., 2] = mag
        flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        left = np.copy(mag)
        left[np.where(ang <= 60)] = 0
        left[np.where(ang >= 90)] = 0
        get_boxes(left, flow)
        windows1 = get_boxes(left, frame1)

        right = np.copy(mag)
        right[np.where(ang >= 30)] = 0
        get_boxes(right, flow)
        windows2 = get_boxes(right, frame1)
        # cv2.imshow('frame1', rgb)
        # cv2.imwrite('_tmp.png'.format(i), rgb)
        run([("frame1.png", np.array(windows1 + windows2))], frame1)
        cv2.imshow('frame1', frame1)
        cv2.imshow('flow', flow)
        cv2.waitKey(0) & 0xff
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main(sys.argv[1:])
