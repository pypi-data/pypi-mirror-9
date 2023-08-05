import numpy as np
from scipy.ndimage.filters import convolve
from solver import NumpySolver


def update(Ix, Iy, It, u, v, ubar, vbar, denom):
    t = (Ix * ubar + Iy * vbar + It) / denom
    u_new = ubar - Ix * t
    v_new = vbar - Iy * t
    err = np.square(u_new - u) + np.square(v_new - v)
    return u_new, v_new, err

alpha = 15.0
alpha2 = alpha ** 2


def compute_denom(Ix, Iy):
    return Ix * Ix + Iy * Iy + alpha2

jacobi = [[0.0, .0025, 0.0],
          [.0025, 0.0, .0025],
          [0.0, .0025, 0.0]]


class HSJacobiNumpy(NumpySolver):
    def solve(self, im0, im1, u, v):
        # Ix, Iy, It = dx(im0, im1), dy(im0, im1), dt(im0, im1)
        Iy, Ix = np.gradient(im1)
        It = im1 - im0
        epsilon = 1e-10

        Ix2 = Ix * Ix 
        IxIy = Ix * Iy
        Iy2 = Iy * Iy

        b0 = Ix * It
        b1 = Iy * It
        b0 = 0.0 - b0
        b1 = 0.0 - b1
        lam4 = .1 * .1
        Dinv0 = 1 / (lam4 + Ix2)
        Dinv1 = 1 / (lam4 + Iy2)
        for i in range(400):
            du_resid = b0 - (convolve(u, jacobi) + IxIy * v) # b-R*x(k)
            dv_resid = b1 - (IxIy * u + convolve(v, jacobi)) # b-R*x(k)
            u = Dinv0 * du_resid
            v = Dinv1 * dv_resid
        return u, v

import cv2

w = 1.9


def get_a_d(im0, i1w, i1wx, u, i1wy, v):
    dif = im0 - i1w + i1wx * u + i1wy * v
    Au = dif * i1wx
    Av = dif * i1wy
    Du = i1wx * i1wx + alpha2
    Dv = i1wy * i1wy + alpha2
    D = i1wy * i1wx
    return Au, Av, Du, Dv, D


def update(u, v, Au, D, Du, Av, Dv):
    ubar = convolve(u, jacobi)
    vbar = convolve(v, jacobi)
    u_old = u
    v_old = v
    u = (1 - w) * u + w * (Au - D * v + alpha * ubar) / Du
    v = (1 - w) * v + w * (Av - D * u + alpha * vbar) / Dv
    err = np.square(u - u_old) + np.square(v - v_old)
    return u, v, err

class HSJacobiNumpyMulti(NumpySolver):
    def solve(self, im0, im1, u, v):
        # Ix, Iy, It = dx(im0, im1), dy(im0, im1), dt(im0, im1)
        Iy, Ix = np.gradient(im1)
        epsilon = (0.0001 ** 2) * np.prod(u.shape)

        ys, xs = np.indices(im1.shape).astype(np.float32)
        for n in range(5):
            i1w = cv2.remap(im1, xs + u, ys + v, cv2.INTER_LINEAR)
            i1wy = cv2.remap(Iy, xs + u, ys + v, cv2.INTER_LINEAR)
            i1wx = cv2.remap(Ix, xs + u, ys + v, cv2.INTER_LINEAR)
            Au, Av, Du, Dv, D = get_a_d(im0, i1w, i1wx, u, i1wy, v)

            for _ in range(100):

                u, v, err = update(u, v, Au, D, Du, Av, Dv)
                if np.sum(err) < epsilon:
                    break
        return u, v


if __name__ == '__main__':
    import cv2
    frame0 = cv2.imread('images/frame0.png')
    frame1 = cv2.imread('images/frame1.png')
    frame0 = cv2.resize(frame0, (384, 288))
    frame1 = cv2.resize(frame1, (384, 288))
    im0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
    im1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    hs_jacobi = HSJacobiNumpy(1, 1.0 / 3.0)

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
