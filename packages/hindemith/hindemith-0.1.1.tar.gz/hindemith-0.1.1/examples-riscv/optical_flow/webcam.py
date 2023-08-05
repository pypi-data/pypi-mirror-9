import cv2
import numpy as np
from hs_jacobi_single import HS_Jacobi
# from hs_jacobi_numpy import HSJacobiNumpy
from ctree.util import Timer

cap = cv2.VideoCapture(0)
# ret = cap.set(3, 640)
# ret = cap.set(4, 480)
ret = cap.set(3, 384)
ret = cap.set(4, 288)

solver = HS_Jacobi(1, .5)
prev_gray = None
while(True):
    with Timer() as t:
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is None:
            prev_gray = gray
            hsv = np.zeros_like(frame)
            continue
        else:
            u = solver(prev_gray, gray)
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
            prev_gray = None
    print("{} fps".format(1/t.interval))

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
