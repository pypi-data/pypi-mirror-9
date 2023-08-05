import cv2
import numpy as np

# cap = cv2.VideoCapture(0)
# ret = cap.set(3,640)
# ret = cap.set(4,480)

shape = [480, 640]
bar_width = 20

def horizontal_bar_image(offset):
    frame = np.zeros(shape).astype(np.uint8)
    for x in range(shape[0]):
        for y in range(offset, offset+bar_width):
            frame[x][y] = 250
    return frame

def vertical_bar_image(offset):
    frame = np.zeros(shape).astype(np.uint8)
    for x in range(offset, offset+bar_width):
        for y in range(shape[1]):
            frame[x][y] = 250
    return frame

image_number = 0
for off in range(0, shape[0]-bar_width, 1):
    gray = vertical_bar_image(off)
    cv2.imshow('frame', gray)
    gray.tofile("/Users/chick/junk/video_frame_{}.raw".format(image_number))
    print("image {}".format(image_number))
    image_number += 1
    if cv2.waitKey(100) & 0x7F == ord('q'):
        break

# When everything done, release the capture
cv2.destroyAllWindows()
exit(0)

image_number = 0
while image_number < 100:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', gray)

    gray.tofile("/Users/chick/junk/video_frame_{}.raw".format(image_number))
    print("image {}".format(image_number))
    image_number += 1
    if cv2.waitKey(100) & 0x7F == ord('q'):
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
cap.release()
cv2.destroyAllWindows()
