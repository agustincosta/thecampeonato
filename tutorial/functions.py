import cv2 as cv
import numpy as np
import sys
from PIL import Image

class preprocessing:

    rows = 0
    columns = 0
    img = 0
    thresh = 0
    gray_img = 0
    deskewed = 0
    denoised = 0
    cleaned = 0
    joined = 0
    height = 0
    width = 0

    def __init__(self, imgPath):
        self.getImage(imgPath)
        self.height, self.width = self.img.shape[:2]

    def getImage(self, imgPath):
        self.img = cv.imread(imgPath)
        if self.img is None:
            sys.exit("Could not open the image")

    def grayscaling(self):
        self.gray_img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)

    def adaptiveThresholding(self):
        self.grayscaling()
        th = cv.adaptiveThreshold(self.gray_img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 389, 2)
        return th

    def deskew(self, image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv.warpAffine(image, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
        return rotated

    def denoise(self):
        self.denoised = cv.fastNlMeansDenoising(self.thresh, None, 100, 21, 49)

    def cleanImage(self):
        kernel = np.ones((3,3),np.uint8)
        dilatedImage = cv.dilate(self.thresh, kernel, None, iterations=1)
        self.cleaned = cv.erode(dilatedImage, kernel, None, iterations=1)

    def joinLetters(self):
        kernel = np.ones((3,3),np.uint8)
        erodedImage = cv.erode(self.cleaned, kernel, None, iterations=1)
        self.joined = cv.dilate(erodedImage, kernel, None, iterations=1)

    def ROI(self):
        ROI= np.array([[(120,self.height),(120,220),(750,220),(750,self.height)]], dtype= np.int32)
        blank= np.zeros_like(self.gray_img)
        region_of_interest= cv.fillPoly(blank, ROI,255)
        region_of_interest_image= cv.bitwise_and(self.gray_img, region_of_interest)


if __name__ == "__main__":

    cv.namedWindow("output", cv.WINDOW_NORMAL)

    functions = preprocessing()
    functions.getImage("macro.jpg")
    #print(functions.gray_img.type())
    functions.thresh = functions.adaptiveThresholding()
    functions.deskewed = functions.deskew(functions.thresh)
    functions.denoise()
    functions.cleanImage()
    functions.joinLetters()
    cv.imshow('output', functions.thresh)
    cv.waitKey(0)
    cv.imwrite('thresholding.jpg', functions.thresh)
    cv.imshow('output', functions.cleaned)
    cv.waitKey(0)
    cv.imwrite('cleaned.jpg', functions.cleaned)
    cv.imshow('output', functions.joined)
    cv.waitKey(0)
    cv.imwrite('joined.jpg', functions.joined)
    