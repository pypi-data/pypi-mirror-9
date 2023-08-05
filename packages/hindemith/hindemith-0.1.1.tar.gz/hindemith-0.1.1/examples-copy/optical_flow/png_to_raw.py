import os
import cv2
import numpy as np
from hs_jacobi_single import HS_Jacobi
import png
import array
import math


class ImageGetter(object):
    def __init__(self):
        self.increment = 1
        self.image_number = -1
        self.count_ascending = True
        self.in_file_template = "examples/optical_flow/images/frame{image_number}.png"
        self.raw_out_file_template = "examples/optical_flow/images/frame{image_number}.gray.raw"
        self.out_file_template = "examples/optical_flow/images/out_frame{image_number}.png"
        self.total_files_read = 0
        self.metadata = None  # we will save the first assuming it is the same for all
        self.width, self.height = None, None

    def make_name(self):
        return self.in_file_template.format(image_number=self.image_number)

    def make_out_name(self):
        return self.out_file_template.format(image_number=self.image_number)

    def make_raw_out_name(self):
        return self.raw_out_file_template.format(image_number=self.image_number)

    def next_image_name(self):
        self.image_number += self.increment
        file_name = self.make_name()
        if not os.path.exists(file_name):
            if self.increment > 0:
                self.increment = -1
                self.image_number -= 2
            else:
                self.increment = 1
                self.image_number = 1
            file_name = self.make_name()
        return file_name

    def read(self):
        file_name = self.next_image_name()
        self.width, self.height, pixels, self.metadata = png.Reader(file_name).read_flat()
        print("image_name {}".format(file_name))
        # print("{")
        # for key, value in self.metadata.items():
        #     print("    {}: {},".format(key, value))
        # print("}")
        ndarray = np.array(pixels).reshape(self.height, self.width, self.metadata['planes']).astype(np.int32)
        self.total_files_read += 1
        if self.total_files_read > 10:
            exit(0)
        return 0, ndarray

    def write_image(self, image_array, out_file):
        m = self.metadata
        print("m {}".format(m))
        writer = png.Writer(self.width, self.height, alpha=m['alpha'], greyscale=m['greyscale'], bitdepth=m['bitdepth'],
                            interlace=m['interlace'], planes=m['planes'])
        output = array.array('B', image_array.reshape(self.width * self.height * m['planes']))
        writer.write_array(out_file, output)

    def write_raw(self, ndarray):
        """
        writes a binary ndarray to the filename with same image number as last read in file
        :param ndarray: should be a image
        """
        file_name = self.make_raw_out_name(self.image_number)
        ndarray.tofile(file_name)


#
#
# cap = cv2.VideoCapture(0)
# ret = cap.set(3, 640)
# ret = cap.set(4, 480)


def rgb2gray(rgb):
    """
    convert image to gray scale
    :param rgb:
    :return:
    """
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.144])


def cart_to_polar_py(x, y):
    """
    works very slowly like cv2.cartToPolar
    :param x:
    :param y:
    :return: as set of magnitudes and angles for every vector from (x, y)
    """
    magnitude = np.zeros_like(x)
    angle = np.zeros_like(x)
    for index0 in range(len(x)):
        for index1 in range(len(x[index0])):
            magnitude[index0][index1] = math.sqrt(x[index0][index1]**2 + y[index0][index1]**2)
            angle[index0][index1] = math.atan2(y[index0][index1], x[index0][index1])*(-180/math.pi)
    return magnitude, angle


def cart_to_polar(x, y):
    """
    works very slowly like cv2.cartToPolar
    :param x:
    :param y:
    :return: as set of magnitudes and angles for every vector from (x, y)
    """
    # x = np.array(x)
    # y = np.array(y)
    magnitude = np.sqrt(np.add(np.multiply(x, x), np.multiply(y, y)))
    angle = np.mod(
        np.add(
            np.multiply(np.arctan2(y, x), 180.0/math.pi).astype(np.uint8),
            360
        ),
        360
    )

    return magnitude, angle


def normalize(x):
    max_x = float(np.amax(x))
    min_x = float(np.amin(x))
    return np.add(np.multiply(x, 1.0 / (max_x-min_x)), -min_x)


def _hsv2rgb(h, v):
    """
    compute an rgb value for hue and value, here saturation is set to max (255)
    :param h: hue, must be in degrees
    :param v: value, must be 0 <= v < 1.0
    :return: red, green, blue
    """
    """
    Expects all HSV values in [0, 1], and returns RGB values in [0, 1].
    """
    s = 255
    c = v * s
    x = c * (1 - abs(h/60.0 % 2 - 1))
    m = v - c
    if h < 60: r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    elif h < 360: r, g, b = c, 0, x
    return r+m, g+m, b+m

hsv2rgb = np.frompyfunc(_hsv2rgb, 2, 3)


if __name__ == '__main__':
    print("{} current directory {}".format(os.path.basename(__file__), os.getcwd()))

    image_getter = ImageGetter()

    solver = HS_Jacobi(1, .5)
    prev_gray = None
    flow_image = None

    while True:
        ret, frame = image_getter.read()
        if flow_image is None:
            flow_image = np.zeros_like(frame).astype(np.uint8)

        gray = rgb2gray(frame).astype(np.uint8)
        cv2.imshow('frame', frame)
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is None:
            prev_gray = gray
            hsv = np.zeros_like(frame).astype(np.uint8)
            continue
        else:
            u = solver(prev_gray, gray)
            value, hue = cart_to_polar(u[0], u[1])
            red, green, blue = flow_image[:, :, 0], flow_image[:, :, 1], flow_image[:, :, 2]

            value = normalize(value)
            hsv2rgb(hue, value, red, green, blue)
            # cv2.imshow('frame', flow_image)

            # mag2, ang2 = cv2.cartToPolar(u[0], u[1], angleInDegrees=True)
            # mag2 = normalize(mag)
            # mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
            # ang = ang*180/np.pi/2
            # hsv[..., 1] = 255
            # hsv[..., 0] = ang
            # hsv[..., 2] = mag
            # flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # cv2.imshow('frame', flow)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            prev_gray = gray

    # When everything done, release the capture
    # cap.release()
    cv2.destroyAllWindows()
