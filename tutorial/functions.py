import cv2 as cv
import numpy as np
import sys
# from PIL import Image
from enum import Enum
import pytesseract
from difflib import SequenceMatcher
import imutils

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
    CFBoxWidthTolerance = 0.20
    CFBoxHeightTolerance = 0.20
    erodeKernelSize = 45
    extentLimit = 0.75
    CFText = "CONSUMO FINAL"
    CFBoxFound = False
    productRegion = 0
    priceRegion = 0
    priceAreaDivisionLim = 0.62


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
        kernel = np.ones((5,5),np.uint8)
        dilatedImage = cv.dilate(self.thresh, kernel, None, iterations=1)
        self.cleaned = cv.erode(dilatedImage, kernel, None, iterations=1)

    def edgeDetection(self):
        self.gray_img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        thresh = cv.threshold(self.gray_img, 180, 255, cv.THRESH_BINARY)[1]
        self.edges = cv.Canny(thresh, self.cannyThresh1, self.cannyThresh2)

    def findPaperEdge(self):
        self.grayscaling()
        self.adaptiveThresholding()
        self.cleanImage()
        self.displayImage(self.cleaned)
        self.joinLetters()
        self.displayImage(self.joined)
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
                savedContour = i
        cv.drawContours(im3, contours, savedContour, (0,255,0), 8, cv.FILLED)
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
        cv.drawContours(im3, contours_poly, -1, (0,0,255), 18, cv.FILLED)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

        rect = cv.minAreaRect(contours_poly)
        if rect[1][0] < rect[1][1]:
            self.croppedImgWidthPx = rect[1][0]
            self.croppedImgHeightPx = rect[1][1]
        else:
            self.croppedImgWidthPx = rect[1][1]
            self.croppedImgHeightPx = rect[1][0]

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
        boxFound = False
        kernel = np.ones((7,7),np.uint8)
        contourImg = cv.erode(self.cropped, kernel, None, iterations=1)
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

            if ((heightOK1 and widthOK1) or (heightOK2 and widthOK2)) and (recCenter[1] < self.croppedImgHeightPx/2):
                text = self.readRegionText(np.int0(cv.boxPoints(CFBox)), self.cropped)
                print(text)
                similarity  = SequenceMatcher(None, text, self.CFText).ratio()
                print(similarity)
                cv.waitKey(0)
                if similarity >= 0.7:
                    print("Box found!")
                    boxFound = True
                    break
            
            i = i + 1

        box = np.int0(cv.boxPoints(CFBox))

        return box, boxFound

    def readRegionText(self, region, image):
        blank = np.zeros_like(image)
        boxRegion = cv.fillConvexPoly(blank, region, 255)
        boxRegionImage = cv.bitwise_and(image, boxRegion)
        kernel = np.ones((3,3),np.uint8)
        boxRegionImage = cv.dilate(boxRegionImage, kernel, None, iterations=1)
        cv.imwrite('textRegion.jpg', boxRegionImage)
        text = pytesseract.image_to_string(boxRegionImage, lang="spa", config='-psm 6 -c tessedit_char_whitelist=12345678ABCDEFGHIJKLMNOPQRSTUVWXYZ., load_system_dawg=false load_freq_dawg=false')
        return text

    def joinLetters(self):
        kernel = np.ones((5,5),np.uint8)
        erodedImage = cv.erode(self.cleaned, kernel, None, iterations=1)
        self.joined = cv.dilate(erodedImage, kernel, None, iterations=1)

    def ROI(self, box):
        #ROI= np.array([[(120,self.height),(120,220),(750,220),(750,self.height)]], dtype= np.int32)
        blank= np.zeros_like(self.gray_img)
        region_of_interest= cv.fillConvexPoly(blank, box,255)
        region_of_interest_image= cv.bitwise_and(self.thresh, region_of_interest)
        return region_of_interest_image

    def extractReadingAreas(self, image, boxFactura, boxCF):
        _, prodAreaLowerLim, prodAreaLeftLim, priceAreaRightLim = self.boxLimits(boxFactura)
        _, prodAreaUpperLim, cfBoxLeft, _ = self.boxLimits(boxCF)
        prodAreaRightLim = round(self.croppedImgWidthPx*self.priceAreaDivisionLim) + prodAreaLeftLim
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
        cv.imshow('output', img)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

    def displayImageBox(self, img, boxPoints):
        im3 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.drawContours(im3, [boxPoints], 0, (0,0,255), 8)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

    def displayImageContours(self, img, contour, idx):
        im3 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.drawContours(im3, contour, idx, (0,0,255), 8)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

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
            np.dstack([edged, edged, edged])
            # clone = np.dstack([edged, edged, edged])
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

if __name__ == "__main__":

    cv.namedWindow("output", cv.WINDOW_NORMAL)

    functions = preprocessing("ti_imposible.jpg", locales.TiendaInglesa)
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

    functions.matchTemplate("tiendainglesa_template.jpg", functions.cropped)

    functions.calculateCFBoxDims()
    CF, functions.CFBoxFound = functions.detectCFBox()
    
    if not functions.CFBoxFound:
        print("-------------NO ENCONTRADO-------------")
        sys.exit()

    im3 = cv.cvtColor(functions.cropped, cv.COLOR_GRAY2BGR)
    cv.drawContours(im3, [CF], 0, (0,0,255), 8)
    cv.imshow('output', im3)
    key = cv.waitKey(0)
    if key == ord('q'):
        sys.exit()

    functions.productRegion, functions.priceRegion = functions.extractReadingAreas(functions.cropped, functions.region, CF)
    cv.drawContours(im3, [functions.productRegion], 0, (0,0,255), 8)
    cv.imshow('output', im3)
    key = cv.waitKey(0)
    cv.drawContours(im3, [functions.priceRegion], 0, (255,0,0), 8)
    cv.imshow('output', im3)
    key = cv.waitKey(0)
    productsText = functions.readRegionText(functions.productRegion, functions.cropped)
    priceText = functions.readRegionText(functions.priceRegion, functions.cropped)

    with open('productsText.txt', 'w') as prodTxtFile:
        prodTxtFile.write(productsText)
    prodTxtFile.close()

    with open('priceText.txt', 'w') as priceTxtFile:
        priceTxtFile.write(priceText)
    priceTxtFile.close()

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