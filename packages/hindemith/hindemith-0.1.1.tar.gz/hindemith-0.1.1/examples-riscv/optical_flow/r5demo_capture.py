"""
Use this to capture a bunch of images

Usage: capture_raw_demo dir height width max_frames
"""
import cv2
import sys
import glob

directory = "." if len(sys.argv) < 2 else sys.argv[1]
height = 144 if len(sys.argv) < 3 else int(sys.argv[2])
width = 192 if len(sys.argv) < 4 else int(sys.argv[3])
max_frames = 15 if len(sys.argv) < 5 else int(sys.argv[4])

print("dir {} height {} width {}".format(directory, height, width))

cap = cv2.VideoCapture(0)
ret = cap.set(3, width)
ret = cap.set(4, height)

image_number = 0
# for i, filename in enumerate(sorted(glob.glob('images/sequence3/image*.png'))):

frames = []
while True:
    ret, frame = cap.read()

    # frame = cv2.imread(filename)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', cv2.resize(gray, (640, 480)))
    frames.append(gray)
    if len(frames) > 15:
        frames.pop(0)
    if cv2.waitKey(100) & 0x7F == ord('q'):
        break

for i, frame in enumerate(frames):
    cv2.imwrite(directory + "/images/demo/image_{}.png".format(i), frame)
    frame.tofile(directory + "/images/demo/video_frame_{}.raw".format(i))
    print("image {}".format(i))
while True:
    for i, frame in enumerate(frames):
        frame = cv2.resize(frame, (640, 480))
        cv2.imshow('frame', frame)

        image_number += 1
        if cv2.waitKey(100) & 0x7F == ord('q'):
            exit()

# When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()
