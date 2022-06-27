import cv2 as cv
# import numpy as np
import sys
import time

img = cv.imread("../Images/DEVOTO/1.jpg")
img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
img = cv.GaussianBlur(img, (7, 7), 0)

c=0

def displayImage(img):
    cv.namedWindow("output", cv.WINDOW_NORMAL)
    cv.imshow('output', img)
    key = cv.waitKey(0)
    if key == ord('q'):
        sys.exit()

#for i in range(100, 200, 5):
start = time.time_ns()
#thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, i, c)
T, binaryThresh = cv.threshold(img, 200, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
mid = time.time_ns()
cv.imwrite("../Images/Prueba/thresh_otsu"+str(998)+".jpg", binaryThresh)
end = time.time_ns()
#displayImage(thresh)
print(999)
print("Tiempo binarizado (%d): %d - Tiempo guardado: %d" % (999, ((mid-start)/1000), ((end-mid)/1000)))
