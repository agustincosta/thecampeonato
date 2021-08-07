import cv2 as cv
import numpy as np
import sys
from PIL import Image
from enum import Enum
import pytesseract
from difflib import SequenceMatcher
import imutils

class OCRFunctions:

    def __init__(self):
        pass

    def readRegionText(self, region, image, filename):
        blank = np.zeros_like(image)
        boxRegion = cv.fillConvexPoly(blank, region, 255)
        boxRegionImage = cv.bitwise_and(image, boxRegion)
        kernel = np.ones((3,3),np.uint8)
        boxRegionImage = cv.dilate(boxRegionImage, kernel, None, iterations=1)
        if not (filename == None):
            cv.imwrite('text' + filename + '.jpg', boxRegionImage)
        ocr_options = '--psm 6 -c preserve_interword_spaces=1 -c tessedit_char_whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$-+:., " load_system_dawg=false load_freq_dawg=false'
        text = pytesseract.image_to_string(boxRegionImage, lang="spa", config=ocr_options)
        return text

    def writeTextFile(self, text, filename):
        with open('../Results/'+filename+'.txt', 'w') as txtFile:
            txtFile.write(text)
        txtFile.close()