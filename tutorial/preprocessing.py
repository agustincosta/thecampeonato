import cv2
import numpy as np
import sys

#img = cv2.imread('image.jpg')

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)
 
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#dilation
def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
    
#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)

#skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

#perspective correction
def perspective_correction(image):
    rows,cols,ch = image.shape
    pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])    #select by hand
    pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    cv2.warpPerspective(image,M,(300,300))

if __name__ == "__main__":
    image = cv2.imread('boleta_frog2.jpg')

    if image is None:
        sys.exit("Could not read the image.")

    gray = get_grayscale(image)
    thresh = thresholding(gray)
    eroded = erode(thresh)
    dilated = dilate(eroded)
    open = opening(gray)
    canned = canny(gray)

    cv2.namedWindow("output", cv2.WINDOW_NORMAL)

    cv2.imshow('output',dilated)
    cv2.waitKey(0)

    cv2.imshow('output',eroded)
    cv2.waitKey(0)

    """ cv2.imshow('image',gray)
    cv2.waitKey(0)

    cv2.imshow('image2',thresh)
    cv2.waitKey(0)

    cv2.imshow('image3',opening)
    cv2.waitKey(0)

    cv2.imshow('image4',canny)
    cv2.waitKey(0) """

    cv2.imwrite('image1.jpg', gray)
    cv2.imwrite('image2.jpg', thresh)
    cv2.imwrite('image3.jpg', open)
    cv2.imwrite('image4.jpg', canned)
    cv2.imwrite('image5.jpg', eroded)