import cv2
import sys
import numpy as np
height = 480
width = 640

directory = "./images/demo" if len(sys.argv) < 2 else sys.argv[1]
height, width = {
    "./images/raw0": (480, 640),
    "./images/raw1": (240, 320),
    "./images/raw2": (144, 192),
    "./images/demo": (144, 192)
}[directory]

while True:
    for i in range(14):
        # ret, frame = cap.read()

        orig = cv2.imread(directory + "/image_{}.png".format(i))
        frame = np.fromfile(directory + "/flow/out_frame{}.raw".format(i + 1),
                            dtype=np.uint8).reshape([height, width, 3])
        frame = cv2.resize(frame, (640, 480))
        orig = cv2.resize(orig, (640, 480))
        cv2.imshow('flow', frame)
        cv2.imshow('orig', orig)

        if cv2.waitKey(100) & 0x7F == ord('q'):
            exit()

# When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()
