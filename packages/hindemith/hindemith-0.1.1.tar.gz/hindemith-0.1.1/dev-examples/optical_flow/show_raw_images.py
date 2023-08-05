import cv2
import numpy as np
import time

# cap = cv2.VideoCapture(0)
# ret = cap.set(3,640)
# ret = cap.set(4,480)

image_number = 0
while image_number < 100:
    gray = np.fromfile("/Users/chick/junk/video_frame_{}.raw".format(image_number), dtype=np.uint8).reshape([480, 640])
    image_number += 1
    print("frame number {}".format(image_number))
    cv2.imshow('frame', gray)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

    # if prev_gray is None:
    #     prev_gray = gray
    #     hsv = np.zeros_like(frame)
    #     continue
    # else:
    #     u = solver(prev_gray, gray)
    #     mag, ang = cv2.cartToPolar(u[0], u[1])
    #     mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    #     ang = ang*180/np.pi/2
    #     hsv[..., 1] = 255
    #     hsv[..., 0] = ang
    #     hsv[..., 2] = mag
    #     flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    #     cv2.imshow('frame', flow)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    #     prev_gray = gray

# When everything done, release the capture
cv2.destroyAllWindows()
