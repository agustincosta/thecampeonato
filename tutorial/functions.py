import cv2 as cv
import numpy as np
import sys
from PIL import Image
from enum import Enum

class locales(Enum):
    TiendaInglesa = 1
    Disco = 2
    Devoto = 3
    Geant = 4
    Kinko = 5
    Frog = 6
    Macro = 7
    Tata = 8


class preprocessing:

    img = 0
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
    local = 0
    consumoFinalBoxWidthPx = 0
    consumoFinalBoxHeightPx = 0
    croppedImgWidthPx = 0
    croppedImgHeightPx = 0
    CFBoxWidthTolerance = 0.15
    CFBoxHeightTolerance = 0.15
    erodeKernelSize = 45
    extentLimit = 0.75


    def __init__(self, imgPath, supermarket):
        self.getImage(imgPath)
        self.local = supermarket
        self.height, self.width = self.img.shape[:2]

    def getImage(self, imgPath):
        self.img = cv.imread(imgPath)
        if self.img is None:
            sys.exit("Could not open the image")

    def grayscaling(self):
        self.gray_img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)

    def adaptiveThresholding(self):
        self.grayscaling()
        self.thresh = cv.adaptiveThreshold(self.gray_img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, self.thresholdingBlockSize, self.thresholdingConstant)

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

    def edgeDetection(self):
        self.gray_img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        thresh = cv.threshold(self.gray_img, 180, 255, cv.THRESH_BINARY)[1]
        self.edges = cv.Canny(thresh, self.cannyThresh1, self.cannyThresh2)

    def findPaperEdge(self):
        self.grayscaling()
        self.adaptiveThresholding()
        cv.imshow('output', self.img)
        cv.waitKey(0)

        kernel = np.ones((self.erodeKernelSize,self.erodeKernelSize),np.uint8)
        eroded = cv.erode(self.thresh, kernel, None, iterations=1)
        cv.imshow('output', eroded)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

        contours, hierarchy = cv.findContours(eroded, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        im3 = cv.cvtColor(eroded, cv.COLOR_GRAY2BGR)

        maxArea = 0
        savedContour = 0
        for i in range(0, len(contours)):
            area = cv.contourArea(contours[i])
            if area > maxArea:
                maxArea = area
                prevContour = savedContour
                savedContour = i
        result = cv.drawContours(im3, contours, savedContour, (0,255,0), 8, cv.FILLED)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()
        """
        lines = cv.HoughLines(im3,1,np.pi/180,200)
        for line in lines:
            rho,theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv.line(im3,(x1,y1),(x2,y2),(0,0,255),2)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()
        """
        contours_poly = cv.approxPolyDP(contours[savedContour], 150, True)
        result = cv.drawContours(im3, contours_poly, -1, (0,0,255), 18, cv.FILLED)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

        rect = cv.minAreaRect(contours_poly)
        self.croppedImgWidthPx = rect[1][0]
        self.croppedImgHeightPx = rect[1][1]

        area = cv.contourArea(contours[savedContour])
        extent = float(area)/(self.croppedImgHeightPx*self.croppedImgWidthPx)
        print(extent)

        if extent < self.extentLimit:
            #find straight lines
            print("Mal detectado")

        box = cv.boxPoints(rect)
        box = np.int0(box)

        cv.drawContours(im3, [box], 0, (0,0,255), 8)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

        return box

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
            sys.exit()

        self.consumoFinalBoxWidthPx = self.croppedImgWidthPx*anchoBoxmm/self.ticketWidthmm
        self.consumoFinalBoxHeightPx = altoBoxmm*self.consumoFinalBoxWidthPx/anchoBoxmm  

    def detectCFBox(self):
        contours, hierarchy = cv.findContours(self.cropped, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
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

            print("W="+str(recWidth)+" H="+str(recHeight))

            if ((heightOK1 and widthOK1) or (heightOK2 and widthOK2)) and (recCenter[1] < self.croppedImgHeightPx/2):
                #CFBox = boundingRect
                break
        
        return CFBox


    def joinLetters(self):
        kernel = np.ones((3,3),np.uint8)
        erodedImage = cv.erode(self.cleaned, kernel, None, iterations=1)
        self.joined = cv.dilate(erodedImage, kernel, None, iterations=1)

    def ROI(self, box):
        #ROI= np.array([[(120,self.height),(120,220),(750,220),(750,self.height)]], dtype= np.int32)
        blank= np.zeros_like(self.gray_img)
        region_of_interest= cv.fillConvexPoly(blank, box,255)
        region_of_interest_image= cv.bitwise_and(self.thresh, region_of_interest)
        return region_of_interest_image

if __name__ == "__main__":

    cv.namedWindow("output", cv.WINDOW_NORMAL)

    functions = preprocessing("tiendainglesa3.jpg", locales.TiendaInglesa)
    """
    #functions.getImage()
    #print(functions.gray_img.type())
    functions.thresh = functions.adaptiveThresholding()
    functions.deskewed = functions.deskew(functions.thresh)
    functions.denoise()
    functions.cleanImage()
    functions.joinLetters()
    cv.imshow('output', functions.thresh)
    cv.waitKey(0)
    cv.imwrite('thresholding.jpg', functions.thresh)
    im2 = functions.thresh
    """
    functions.region = functions.findPaperEdge()
    functions.cropped = functions.ROI(functions.region)
    cv.imshow('output', functions.cropped)
    key = cv.waitKey(0)
    if key == ord('q'):
        sys.exit()
    cv.imwrite('cropped.jpg', functions.cropped)
    functions.calculateCFBoxDims()
    CF = functions.detectCFBox()
    
    box = cv.boxPoints(CF)
    box = np.int0(box)
    im3 = cv.cvtColor(functions.cropped, cv.COLOR_GRAY2BGR)
    cv.drawContours(im3, [box], 0, (0,0,255), 8)
    cv.imshow('output', im3)
    key = cv.waitKey(0)
    if key == ord('q'):
        sys.exit()
    """
    functions.edgeDetection()
    cv.imshow('output', functions.edges)
    cv.waitKey(0)
    cv.imwrite('canny.jpg', functions.edges)

    
    cv.imshow('output', functions.cleaned)
    cv.waitKey(0)
    # ROI= np.array([[(120,functions.height),(120,220),(750,220),(750,functions.height)]], dtype= np.int32)
    # draw = cv.polylines(functions.cleaned, ROI, True, (0,255,0), thickness=3)
    # cv.imshow('output', draw)
    # cv.waitKey(0)
    cv.imwrite('cleaned.jpg', functions.cleaned)
    cv.imshow('output', functions.joined)
    cv.waitKey(0)
    cv.imwrite('joined.jpg', functions.joined)
    """