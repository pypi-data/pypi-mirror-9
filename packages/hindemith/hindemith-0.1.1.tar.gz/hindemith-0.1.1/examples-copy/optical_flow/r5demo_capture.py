"""
Use this to capture a bunch of images

Usage: capture_raw_demo dir height width max_frames
"""
import cv2
import sys

directory = "." if len(sys.argv) < 2 else sys.argv[1]
height = 480 if len(sys.argv) < 3 else int(sys.argv[2])
width = 640 if len(sys.argv) < 4 else int(sys.argv[3])
max_frames = 20 if len(sys.argv) < 5 else int(sys.argv[4])

print("dir {} height {} width {}".format(directory, height, width))

cap = cv2.VideoCapture(0)
ret = cap.set(3, width)
ret = cap.set(4, height)

image_number = 0
while image_number < max_frames:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', gray)

    gray.tofile(directory + "/video_frame_{}.raw".format(image_number))
    print("image {}".format(image_number))
    image_number += 1
    if cv2.waitKey(100) & 0x7F == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
