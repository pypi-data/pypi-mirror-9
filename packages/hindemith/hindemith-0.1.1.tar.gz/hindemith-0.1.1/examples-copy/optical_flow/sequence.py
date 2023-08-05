import cv2
import numpy as np
from hs_jacobi_single import HS_Jacobi
from ctree.util import Timer

solver = HS_Jacobi(1, .5)
prev_gray = None
import glob

for i, filename in enumerate(sorted(glob.glob('images/sequence1/image*.png'))):
    frame = cv2.imread(filename)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if prev_gray is None:
        prev_gray = gray
        hsv = np.zeros_like(frame)
        continue
    else:
        with Timer() as t:
            u = solver(prev_gray, gray)
        print(t.interval)
        mag, ang = cv2.cartToPolar(u[0], u[1])
        mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        ang = ang*180/np.pi/2
        hsv[..., 1] = 255
        hsv[..., 0] = ang
        hsv[..., 2] = mag
        flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        cv2.imshow('frame', flow)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        prev_gray = gray

# When everything done, release the capture
cv2.destroyAllWindows()
