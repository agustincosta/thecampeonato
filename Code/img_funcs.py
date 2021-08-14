import cv2 as cv
import numpy as np
import sys
from PIL import Image
from enum import Enum
from difflib import SequenceMatcher
import imutils
from ocr_funcs import OCRFunctions

class locales(Enum):
    TiendaInglesa = 1
    Disco = 2
    Devoto = 3
    Geant = 4
    Kinko = 5
    Frog = 6
    Macro = 7
    Tata = 8

class imageFunctions:

    img = 0
    adaptThresh = 0
    binaryThresh = 0
    thresh = 0
    gray_img = 0
    deskewed = 0
    denoised = 0
    cleaned = 0
    joined = 0
    height = 0
    width = 0
    thresholdingBlockSize = 3009
    thresholdingConstant = 2
    cannyThresh1 = 100
    cannyThresh2 = 200
    binaryLimit = 170
    edges = 0
    region = 0
    cropped = 0
    ticketWidthmm = 79
    consumoFinalTIBoxWidthmm = 65
    consumoFinalTIBoxHeightmm = 9.5
    consumoFinalVarBoxWidthmm = 70
    consumoFinalVarBoxHeightmm = 12
    consumoFinalDevSBoxWidthmm = 59
    consumoFinalDevSBoxHeightmm = 9.5
    consumoFinalDevLBoxWidthmm = 59
    consumoFinalDevLBoxHeightmm = 15
    consumoFinalMacroBoxHeightmm = 11
    consumoFinalMacroBoxWidthmm = 31.5
    local = 0
    consumoFinalBoxWidthPx = 0
    consumoFinalBoxHeightPx = 0
    croppedImgWidthPx = 0
    croppedImgHeightPx = 0
    CFBoxWidthTolerance = 0.20
    CFBoxHeightTolerance = 0.20
    erodeKernelSize = 45
    extentLimit = 0.75
    CFText = "CONSUMO FINAL"
    CFBoxFound = False
    productRegion = 0
    priceRegion = 0
    priceAreaDivisionLim = 0.62
    CFBox = 0
    stopProcess = False

    def __init__(self, imgPath, supermarket):
        self.getImage(imgPath)
        self.local = supermarket
        self.height, self.width = self.img.shape[:2]
        self.croppedImgHeightPx = self.height
        self.croppedImgWidthPx = self.width
        self.stopProcess = False

    def getImage(self, imgPath):
        self.img = cv.imread(imgPath)
        if self.img is None:
            sys.exit("Could not open the image")

    def grayscaling(self, image):
        gray_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        return gray_img

    def adaptiveThresholding(self, image):
        grayscale = self.grayscaling(image)
        adaptThresh = cv.adaptiveThreshold(grayscale, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, self.thresholdingBlockSize, self.thresholdingConstant)
        return adaptThresh

    def normalThresholding(self, image):
        grayscale = self.grayscaling(image)
        _, binaryThresh = cv.threshold(grayscale, self.binaryLimit, 255, cv.THRESH_BINARY)
        return binaryThresh

    def cleanImage(self, image):
        kernel = np.ones((5,5),np.uint8)
        dilatedImage = cv.dilate(image, kernel, None, iterations=1)
        cleaned = cv.erode(dilatedImage, kernel, None, iterations=1)
        return cleaned

    def calculateCFBoxDims(self):
        anchoBoxmm = 0
        altoBoxmm = 0
        if self.local == locales.TiendaInglesa:
            anchoBoxmm = self.consumoFinalTIBoxWidthmm
            altoBoxmm = self.consumoFinalTIBoxHeightmm
        elif self.local == locales.Geant:
            anchoBoxmm = self.consumoFinalVarBoxWidthmm
            altoBoxmm = self.consumoFinalVarBoxHeightmm
        elif self.local == locales.Disco:
            anchoBoxmm = self.consumoFinalVarBoxWidthmm
            altoBoxmm = self.consumoFinalVarBoxHeightmm
        elif self.local == locales.Devoto:
            anchoBoxmm = self.consumoFinalDevSBoxWidthmm
            altoBoxmm = (self.consumoFinalDevSBoxHeightmm + self.consumoFinalDevLBoxHeightmm)/2
            self.CFBoxHeightTolerance = 0.35
        elif self.local == locales.Frog:
            anchoBoxmm = self.consumoFinalVarBoxWidthmm
            altoBoxmm = self.consumoFinalTIBoxHeightmm
        elif self.local == locales.Kinko:
            anchoBoxmm = self.consumoFinalVarBoxWidthmm
            altoBoxmm = self.consumoFinalTIBoxHeightmm
        elif self.local == locales.Tata:
            anchoBoxmm = self.consumoFinalVarBoxWidthmm
            altoBoxmm = self.consumoFinalTIBoxHeightmm
        elif self.local == locales.Macro:
            anchoBoxmm = self.consumoFinalMacroBoxWidthmm
            altoBoxmm = self.consumoFinalMacroBoxHeightmm

        self.consumoFinalBoxWidthPx = self.width*anchoBoxmm/self.ticketWidthmm
        self.consumoFinalBoxHeightPx = altoBoxmm*self.consumoFinalBoxWidthPx/anchoBoxmm 

    def detectCFBox(self, image):
        boxFound = False
        kernel = np.ones((15,15),np.uint8)
        contourImg = cv.erode(image, kernel, None, iterations=1)
        #self.displayImage(contourImg)
        contours, hierarchy = cv.findContours(contourImg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        recCenter = 0
        recWidth = 0
        recHeight = 0
        CFBox = 0
        widthHighLimit = self.consumoFinalBoxWidthPx*(1+self.CFBoxWidthTolerance)
        widthLowLimit = self.consumoFinalBoxWidthPx*(1-self.CFBoxWidthTolerance)
        heightHighLimit = self.consumoFinalBoxHeightPx*(1+self.CFBoxHeightTolerance)
        heightLowLimit = self.consumoFinalBoxHeightPx*(1-self.CFBoxHeightTolerance)
        print("Limits W=("+str(widthLowLimit)+", "+str(widthHighLimit)+") H=("+str(heightLowLimit)+", "+str(heightHighLimit)+")")
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

        #self.displayImageContours(contourImg, contours, -1)
        i = 0

        for c in contours:
            simplifiedContour = cv.approxPolyDP(c, 3, True)
            boundingRect = cv.minAreaRect(simplifiedContour)
            CFBox = boundingRect
            recCenter = boundingRect[0]
            recWidth = boundingRect[1][0]
            recHeight = boundingRect[1][1]
            widthOK1 = (recWidth < widthHighLimit) and (recWidth > widthLowLimit)
            heightOK1 = (recHeight < heightHighLimit) and (recHeight > heightLowLimit)
            widthOK2 = (recWidth < heightHighLimit) and (recWidth > heightLowLimit)
            heightOK2 = (recHeight < widthHighLimit) and (recHeight > widthLowLimit)

            #print("W="+str(recWidth)+" H="+str(recHeight))
            #self.displayImageContours(contourImg, contours, i)

            if ((heightOK1 and widthOK1) or (heightOK2 and widthOK2)) and (recCenter[1] < self.height/2):
                text = OCRFunctions.readRegionText(OCRFunctions, np.int0(cv.boxPoints(CFBox)), image, "cfBox", True)
                #print(text)
                similarity  = SequenceMatcher(None, text, self.CFText).ratio()
                #print(similarity)
                #cv.waitKey(0)
                if similarity >= 0.7:
                    print("Box found!")
                    boxFound = True
                    break
            
            i = i + 1

        box = np.int0(cv.boxPoints(CFBox))

        return box, boxFound
    
    def joinLetters(self):
        kernel = np.ones((5,5),np.uint8)
        erodedImage = cv.erode(self.cleaned, kernel, None, iterations=1)
        self.joined = cv.dilate(erodedImage, kernel, None, iterations=1)
        return self.joined

    def ROI(self, box):
        #ROI= np.array([[(120,self.height),(120,220),(750,220),(750,self.height)]], dtype= np.int32)
        blank= np.zeros_like(self.gray_img)
        region_of_interest= cv.fillConvexPoly(blank, box,255)
        region_of_interest_image= cv.bitwise_and(self.thresh, region_of_interest)
        return region_of_interest_image

    def extractReadingAreas(self, image, boxFactura, boxCF):
        _, prodAreaLowerLim, prodAreaLeftLim, priceAreaRightLim = self.boxLimits(boxFactura)
        _, prodAreaUpperLim, cfBoxLeft, _ = self.boxLimits(boxCF)
        if (self.local != locales.Macro):
            prodAreaRightLim = round(self.croppedImgWidthPx*self.priceAreaDivisionLim) + prodAreaLeftLim
        else:
            prodAreaRightLim = round(self.width/2)
        priceAreaLeftLim = prodAreaRightLim
        priceAreaUpperLim = prodAreaUpperLim
        priceAreaLowerLim = prodAreaLowerLim
        productsBox = np.array([[prodAreaLeftLim, prodAreaLowerLim], [prodAreaLeftLim, prodAreaUpperLim], [prodAreaRightLim, prodAreaUpperLim], [prodAreaRightLim, prodAreaLowerLim]])
        pricesBox = np.array([[priceAreaLeftLim, priceAreaLowerLim], [priceAreaLeftLim, priceAreaUpperLim], [priceAreaRightLim, priceAreaUpperLim], [priceAreaRightLim, priceAreaLowerLim]])
        
        return productsBox, pricesBox

    def boxLimits(self, boxPoints):
        lower = max(boxPoints[:,1])
        upper = min(boxPoints[:,1])
        left = min(boxPoints[:,0])
        right = max(boxPoints[:,0])
        return upper, lower, left, right
    
    def displayImage(self, img):
        cv.namedWindow("output", cv.WINDOW_NORMAL)
        cv.imshow('output', img)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

    def displayImageBox(self, img, boxPoints):
        im3 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.drawContours(im3, [boxPoints], 0, (0,0,255), 8)
        cv.namedWindow("output", cv.WINDOW_NORMAL)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

    def displayImageContours(self, img, contour, idx):
        im3 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.drawContours(im3, contour, idx, (0,0,255), 8)
        cv.namedWindow("output", cv.WINDOW_NORMAL)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

    def saveImage(self, img, filename):
        cv.imwrite(filename, img)

    def matchTemplate(self, temp, img):
        template = cv.imread(temp)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        template = cv.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        cv.imshow("Template", template)
        found = None

        for scale in np.linspace(0.2, 2.0, 40)[::-1]:
            resized = imutils.resize(img, width=int(img.shape[1]*scale))
            r = img.shape[1]/float(resized.shape[1])
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break
            edged = cv.Canny(resized, 50, 200)
            result = cv.matchTemplate(edged, template, cv.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv.minMaxLoc(result)
            clone = np.dstack([edged, edged, edged])
            #cv.rectangle(clone, (maxLoc[0], maxLoc[1]),(maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            #cv.namedWindow("Visualize", cv.WINDOW_NORMAL)
            #cv.imshow("Visualize", clone)
            #cv.waitKey(0)

            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        img_color = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.rectangle(img_color, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv.imshow("Image", img_color)
        cv.waitKey(0)
        cv.imwrite('logo_found.jpg', img_color)

    def imageConditioning(self, dir, filename):
        #self.displayImage(self.img)
        self.binaryThresh = self.normalThresholding(self.img)
        #self.binaryThresh = self.adaptiveThresholding(self.img)
        #self.displayImage(binaryThresh)
        self.saveImage(self.binaryThresh, dir+"/binarized_"+filename)
        self.cleaned = self.cleanImage(self.binaryThresh)
        #self.displayImage(self.cleaned)
        self.calculateCFBoxDims()
        self.CFBox, CFBoxFound = self.detectCFBox(self.cleaned)

        if not CFBoxFound:
            #print("-------------NO ENCONTRADO-------------")
            #sys.exit()
            self.stopProcess = True
            raise RuntimeError("-------------NO ENCONTRADO-------------")

        return CFBoxFound, self.cleaned

    def textRegions(self, image):
        self.region =np.array([[0, self.height], [0, 0], [self.width, 0], [self.width, self.height]])
        self.productRegion, self.priceRegion = self.extractReadingAreas(image, self.region, self.CFBox)
        return self.productRegion, self.priceRegion
