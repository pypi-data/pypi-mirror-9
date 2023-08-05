import numpy as np
import cv2


def py_th(rho_elt, gradient_elt, delta_elt, u_elt):
    thresh = l * theta * gradient_elt
    if rho_elt < -thresh:
        return l * theta * delta_elt + u_elt
    elif rho_elt > thresh:
        return -l * theta * delta_elt + u_elt
    elif gradient_elt > 1e-10:
        return -rho_elt / gradient_elt * delta_elt + u_elt
    else:
        return 0


py_thresh = np.vectorize(py_th, otypes=[np.float32])


def py_threshold(u1, u2, rho_c, gradient, I1wx, I1wy):
    rho = rho_c + I1wx * u1 + I1wy * u2
    v1 = py_thresh(rho, gradient, I1wx, u1)
    v2 = py_thresh(rho, gradient, I1wy, u2)
    return v1, v2


def py_forward_gradient(m):
    dx, dy = np.zeros_like(m), np.zeros_like(m)
    dy[:-1, ...] = m[1:, ...] - m[:-1, ...]
    dx[..., :-1] = m[..., 1:] - m[..., :-1]
    return dx, dy


def py_divergence(v1, v2):
    div = np.zeros_like(v1)
    div[1:, 1:] = v2[1:, 1:] - v2[:-1, 1:] + v1[1:, 1:] - v1[1:, :-1]
    div[1:, 0] = v2[1:, 0] - v2[:-1, 0] + v1[1:, 0]
    div[0, 1:] = v2[0, 1:] + v1[0, 1:] - v1[0, :-1]
    # div[0, 0] = v1[0, 0] + v2[0, 0]
    return div


def warp(im, f1, f2):
    return cv2.remap(im, f1, f2, cv2.INTER_LINEAR)


def py_flow(I0, I1, u1, u2):
    p11 = np.zeros(I1.shape, dtype=np.float32)
    p12 = np.zeros(I1.shape, dtype=np.float32)
    p21 = np.zeros(I1.shape, dtype=np.float32)
    p22 = np.zeros(I1.shape, dtype=np.float32)
    i1y, i1x = centered_gradient(I1)
    i1x = i1x.astype(np.float32)
    i1y = i1y.astype(np.float32)
    indices = np.indices(u1.shape).astype(np.float32)
    for w in range(num_warps):
        _f1, _f2 = build_flow_map(indices, u1, u2)
        i1w = warp(I1, _f1, _f2)
        i1wx = warp(i1x, _f1, _f2)
        i1wy = warp(i1y, _f1, _f2)
        grad = np.square(i1wx) + np.square(i1wy)
        rho_c = i1w - i1wx * u1 - i1wy * u2 - I0
        n0 = 0
        error = sys.maxint
        while n0 < n_outer and error > epsilon * epsilon * I0.size:
            # u1 = cv2.medianBlur(u1, median_filtering)
            # u2 = cv2.medianBlur(u2, median_filtering)
            n1 = 0
            while n1 < n_inner and error > epsilon * epsilon * I0.size:
                v1, v2 = py_threshold(u1, u2, rho_c, grad, i1wx, i1wy)
                div_p1 = py_divergence(p11, p12)
                div_p2 = py_divergence(p21, p22)
                u1_old = u1
                u2_old = u2
                u1 = v1 + div_p1 * theta
                u2 = v2 + div_p2 * theta
                error = np.sum(np.square(u1 - u1_old) + np.square(u2 - u2_old))
                u1x, u1y = py_forward_gradient(u1)
                u2x, u2y = py_forward_gradient(u2)
                ng1 = 1.0 + tau / theta * np.sqrt(np.square(u1x) +
                                                  np.square(u1y))
                ng2 = 1.0 + tau / theta * np.sqrt(np.square(u2x) +
                                                  np.square(u2y))
                p11 = (p11 + tau / theta * u1x) / ng1
                p12 = (p12 + tau / theta * u1y) / ng1
                p21 = (p21 + tau / theta * u2x) / ng2
                p22 = (p22 + tau / theta * u2y) / ng2
                n1 += 1
            n0 += 1
    return u1, u2


def py_tvl1(im0, im1):
    im0 = im0.astype(np.float32)
    im1 = im1.astype(np.float32)
    # im0 = (cv2.GaussianBlur(im0))
    # im1 = (cv2.GaussianBlur(im1))
    im0_pyr = pyr_down(im0, n_scales, n)
    im1_pyr = pyr_down(im1, n_scales, n)
    u1 = np.zeros(im0_pyr[-1].shape, dtype=np.float32)
    u2 = np.zeros(im0_pyr[-1].shape, dtype=np.float32)
    for s in reversed(range(n_scales)):
        u1, u2, = py_flow(im0_pyr[s], im1_pyr[s], u1, u2)
        if s > 0:
            u1 = pyr_up(u1, im0_pyr[s - 1].shape[::-1]) * (1.0 / n)
            u2 = pyr_up(u2, im0_pyr[s - 1].shape[::-1]) * (1.0 / n)
    return u1, u2

