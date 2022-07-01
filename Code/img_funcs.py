import cv2 as cv
import numpy as np
import sys
from PIL import Image
from enum import Enum
from difflib import SequenceMatcher
import imutils
from ocr_funcs import OCRFunctions
import matplotlib.pyplot as plt
import pytesseract
from pytesseract import Output

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
    otsuThresh = 0
    gray_img = 0
    deskewed = 0
    denoised = 0
    cleaned = 0
    joined = 0
    height = 0
    width = 0
    thresholdingBlockSize = 3309
    thresholdingConstant = 20
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

    def __init__(self, imgPath:str, supermarket:locales):
        """Inicializacion de clase. Lee imagen y obtiene parametros basicos

        Args:
            imgPath (str): Ruta de imagen a leer de archivo
            supermarket (locales): Enum de local al que pertenece la factura
        """        
        self.getImage(imgPath)
        self.local = supermarket
        self.height, self.width = self.img.shape[:2]
        self.croppedImgHeightPx = self.height
        self.croppedImgWidthPx = self.width
        self.stopProcess = False

    def getImage(self, imgPath:str):
        """Lee imagen de archivo

        Args:
            imgPath (str): Ruta de imagen
        """        
        self.img = cv.imread(imgPath)
        if self.img is None:
            sys.exit("Could not open the image")

    def scaling(self, image:cv.Mat, scale=2) -> cv.Mat:
        """Escala imagen por el factor dado

        Args:
            image (cv.Mat): Imagen a escalar
            scale (int, optional): Factor de escalado. Defaults to 2.

        Returns:
            cv.Mat: Imagen escalada
        """              
        self.height = self.height*scale
        self.width = self.width*scale
        return cv.resize(image, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC)

    def grayscaling(self, image:cv.Mat) -> cv.Mat:
        """Convierte imagen a escala de grises

        Args:
            image (cv.Mat): Imagen a color

        Returns:
            cv.Mat: Imagen en escala de grises
        """        
        gray_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        return gray_img

    def gaussianBlur(self, image:cv.Mat) -> cv.Mat:
        """Aplica filtro gaussiano para suavizar pixeles con kernel predefinido de 7x7

        Args:
            image (cv.Mat): Imagen a filtrar

        Returns:
            cv.Mat: Imagen filtrada
        """        
        return cv.GaussianBlur(image, (7, 7), 0)

    def filtering(self, image:cv.Mat) -> cv.Mat:
        """Aplica filtro bilateral a imagen para suavizar con diametro 19

        Args:
            image (cv.Mat): Imagen a filtrar

        Returns:
            (cv.Mat): Imagen filtrada
        """        
        bilateral = cv.bilateralFilter(image, 19, 100, 100)
        return bilateral

    def adaptiveThresholding(self, image:cv.Mat) -> cv.Mat:
        """Binarizado de imagen con umbral adaptivo. Tamaño de area de umbral dado por variables globales de clase

        Args:
            image (cv.Mat): Imagen en escala de grises

        Returns:
            cv.Mat: Imagen en blanco y negro
        """        
        adaptThresh = cv.adaptiveThreshold(image, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, self.thresholdingBlockSize, self.thresholdingConstant)
        return adaptThresh

    def normalThresholding(self, image:cv.Mat) -> cv.Mat:
        """Binarizado con umbral fijo

        Args:
            image (cv.Mat): Imagen en escala de grises

        Returns:
            cv.Mat: Imagen en blanco y negro
        """        
        grayscale = self.grayscaling(image)
        _, binaryThresh = cv.threshold(grayscale, self.binaryLimit, 255, cv.THRESH_BINARY)
        return binaryThresh

    def OtsuThresholding(self, image:cv.Mat) -> cv.Mat:
        """Binarizado con metodo Otsu. Mejor que umbral fijo y mas rapido que adaptivo

        Args:
            image (cv.Mat): Imagen en escala de grises

        Returns:
            cv.Mat: Imagen en blanco y negro
        """        
        T, binaryThresh = cv.threshold(image, self.binaryLimit, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
        return binaryThresh

    def cleanImage(self, image:cv.Mat) -> cv.Mat:
        """Erode y dilate para eliminar puntos sueltos y unir lineas cortadas

        Args:
            image (cv.Mat): Imagen de entrada

        Returns:
            cv.Mat: Imagen restaurada
        """        
        if self.local==locales.Macro:
            kernel = np.ones((3,3),np.uint8)
        else:
            kernel = np.ones((9,9),np.uint8)
        eroded = cv.erode(image, kernel, None, iterations=1)
        dilatedImage = cv.dilate(eroded, kernel, None, iterations=1)   
        return dilatedImage

    def getSkewAngle(self, image:cv.Mat) -> float:
        """Obtiene angulo de orientacion de imagen a partir de parrafos y otros bloques

        Args:
            image (cv.Mat): Imagen de entrada

        Returns:
            float: Angulo de orientacion
        """        
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (30, 5))
        dilate = cv.dilate(image, kernel, iterations=5)

        # Find all contours
        contours, hierarchy = cv.findContours(dilate, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv.contourArea, reverse = True)

        # Find largest contour and surround in min area box
        largestContour = contours[0]
        minAreaRect = cv.minAreaRect(largestContour)

        # Determine the angle. Convert it to the value that was originally used to obtain skewed image
        angle = minAreaRect[-1]
        if angle < -45:
            angle = 90 + angle
        
        return -1.0 * angle
        
    def rotateImage(self, image:cv.Mat, angle: float) -> cv.Mat: 
        """Rotacion de imagen por angulo dado

        Args:
            image (cv.Mat): Imagen a rotar
            angle (float): Angulo de rotacion

        Returns:
            cv.Mat: Imagen rotada
        """        
        newImage = image.copy()
        (h, w) = newImage.shape[:2]
        center = (w // 2, h // 2)
        M = cv.getRotationMatrix2D(center, angle, 1.0)
        newImage = cv.warpAffine(newImage, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
        return newImage

    def skewCorrection(self, image:cv.Mat) -> cv.Mat:
        """Corrige la rotacion de la imagen para que este derecha

        Args:
            image (cv.Mat): Imagen mal orientada

        Returns:
            cv.Mat: Imagen derecha
        """        
        rotationAngle = self.getSkewAngle(image)
        return self.rotateImage(image, rotationAngle)
   
    def perspectiveCorrection(self, image):
        #dewarp
        return image

    def calculateCFBoxDims(self):
        """Calcula dimensiones en pixeles de caja de "CONSUMO FINAL" en imagen dependiendo del local
        """        
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

    def detectCFBox(self, image:cv.Mat):
        """Detecta caja de "CONSUMO FINAL" en ticket y obtiene su bounding box

        Args:
            image (cv.Mat): Imagen de ticket

        Returns:
            box (cv.boxPoints): Extremos de caja
            boxFound (bool): Caja encontrada
        """        
        boxFound = False
        kernel = np.ones((15,30),np.uint8)
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
        """Erode y dilate para juntar lineas cortadas por errores de impresion o foto

        Returns:
            cv.Mat: Imagen corregida
        """        
        kernel = np.ones((5,5),np.uint8)
        erodedImage = cv.erode(self.cleaned, kernel, None, iterations=1)
        self.joined = cv.dilate(erodedImage, kernel, None, iterations=1)
        return self.joined

    def ROI(self, box):
        """Recorta region de interes de imagen 

        Args:
            box (_type_): Extremos de region

        Returns:
            _type_: _description_
        """        
        #ROI= np.array([[(120,self.height),(120,220),(750,220),(750,self.height)]], dtype= np.int32)
        blank= np.zeros_like(self.gray_img)
        region_of_interest= cv.fillConvexPoly(blank, box,255)
        region_of_interest_image= cv.bitwise_and(self.thresh, region_of_interest)
        return region_of_interest_image

    def extractReadingAreas(self, boxFactura):
        """Obtiene dos regiones, area de productos y area de precios a partir de la region de interes de la factura

        Args:
            boxFactura (np.array): Extremos de region de interes

        Returns:
            productsBox, pricesBox (np.array): Extremos de regiones de productos y precios
        """        
        prodAreaUpperLim, prodAreaLowerLim, prodAreaLeftLim, priceAreaRightLim = self.boxLimits(boxFactura)
        if (self.local != locales.Macro):
            prodAreaRightLim = round(self.croppedImgWidthPx*self.priceAreaDivisionLim) + prodAreaLeftLim
        else:
            prodAreaRightLim = round(self.width*0.6)
        priceAreaLeftLim = prodAreaRightLim
        priceAreaUpperLim = prodAreaUpperLim
        priceAreaLowerLim = prodAreaLowerLim
        productsBox = np.array([[prodAreaLeftLim, prodAreaLowerLim], [prodAreaLeftLim, prodAreaUpperLim], [prodAreaRightLim, prodAreaUpperLim], [prodAreaRightLim, prodAreaLowerLim]])
        pricesBox = np.array([[priceAreaLeftLim, priceAreaLowerLim], [priceAreaLeftLim, priceAreaUpperLim], [priceAreaRightLim, priceAreaUpperLim], [priceAreaRightLim, priceAreaLowerLim]])
        
        return productsBox, pricesBox

    def boxLimits(self, boxPoints):
        """Obtiene los limites de una caja (arriba, abajo, izquierda, derecha)

        Args:
            boxPoints (np.array): Extremos de region

        Returns:
            upper, lower, left, right (int): Pixeles
        """        
        lower = max(boxPoints[:,1])
        upper = min(boxPoints[:,1])
        left = min(boxPoints[:,0])
        right = max(boxPoints[:,0])
        return upper, lower, left, right
    
    def displayImage(self, img, show=True):
        """Muestra imagen en popup

        Args:
            img (cv.Mat): Imagen a mostrar
            show (bool, optional): Mostrar o no. Defaults to True.
        """        
        if show:
            cv.namedWindow("output", cv.WINDOW_NORMAL)
            cv.imshow('output', img)
            key = cv.waitKey(0)
            if key == ord('q'):
                sys.exit()
        else:
            pass

    def displayImageBox(self, img, boxPoints):
        """Muestra imagen con caja dibujada

        Args:
            img (cv.Mat): Imagen
            boxPoints (np.array): Extremos de caja
        """        
        im3 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.drawContours(im3, [boxPoints], 0, (0,0,255), 8)
        cv.namedWindow("output", cv.WINDOW_NORMAL)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

    def displayImageContours(self, img, contour, idx):
        """Muestra imagen con contornos dibujados

        Args:
            img (cv.Mat): Imagen
            contour (cv.contour): Lista de figuras geometricas a dibujar
            idx (int): Indice de cual dibujar, -1 = todas
        """        
        im3 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.drawContours(im3, contour, idx, (0,0,255), 8)
        cv.namedWindow("output", cv.WINDOW_NORMAL)
        cv.imshow('output', im3)
        key = cv.waitKey(0)
        if key == ord('q'):
            sys.exit()

    def saveImage(self, img, filename):
        """Guarda imagen a archivo

        Args:
            img (cv.Mat): Imagen
            filename (str): Nombre y ruta de archivo
        """        
        cv.imwrite(filename, img)

    def matchTemplate(self, temp:cv.Mat, img:cv.Mat):
        """Matchea template dentro de una imagen. Se usa para buscar logo de super en ticket

        Args:
            temp (cv.Mat): Template
            img (cv.Mat): Imagen
        """        
        template = cv.imread(temp)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        template = cv.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        #cv.imshow("Template", template)
        found = None

        for scale in np.linspace(0.75, 1.25, 10)[::-1]:
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
                print(r, scale)

        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        img_color = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        cv.rectangle(img_color, (startX, startY), (endX, endY), (0, 0, 255), 2)
        self.displayImage(img_color)
        #cv.imshow("Image", img_color)
        #cv.waitKey(0)
        cv.imwrite('logo_found.jpg', img_color)

    def textRegions(self, image:cv.Mat):
        """Obtiene regiones para OCR

        Args:
            image (cv.Mat): Imagen

        Returns:
            self.productRegion, self.priceRegion, self.region (np.array): Regiones de producto, precio y ticket completo
        """        
        self.region =np.array([[0, self.height], [0, 0], [self.width, 0], [self.width, self.height]])
        self.productRegion, self.priceRegion = self.extractReadingAreas(image, self.region)
        return self.productRegion, self.priceRegion, self.region

    def dprint(self, text, cond:bool):
        """Debug print condicional

        Args:
            text (Any): Data
            cond (bool): Imprimir o no
        """        
        if cond:
            print(text)
        else:
            pass

    def dsaveImage(self, img:cv.Mat, filename:str, cond:bool):
        """Debug save image condicional

        Args:
            img (cv.Mat): Imagen a guardar
            filename (str): Nombre del archivo con ruta y extension
            cond (bool): Guardar o no
        """        
        if cond:
            self.saveImage(img, filename)
        else:
            pass    

    def plot_rgb(self, image):
        plt.figure(figsize=(16,10))
        return plt.imshow(cv.cvtColor(image, cv.COLOR_BGR2RGB))

    def imagePreprocessing(self, image:cv.Mat, showResults:bool, dir:str, filename:str) -> cv.Mat:
        """Funcion de preprocesamiento de imagen para OCR. Encadena varias funciones anteriores para lograr una imagen legible

        Args:
            image (cv.Mat): Imagen de entrada
            showResults (bool): Mostrar resultados intermedios
            dir (str): Directorio de imagen (solo directorio, no nombre)
            filename (str): Nombre de archivo (con extension) para guardar resultado

        Returns:
            cv.Mat: Imagen preprocesada
        """        
        resized = self.scaling(image)
        self.dprint("Resized", showResults)
        #self.dsaveImage(resized, "Resized.jpg", showResults)
        grayscale = self.grayscaling(resized)
        self.dprint("Grayscale", showResults)
        #self.dsaveImage(grayscale, "Grayscale.jpg", showResults)
        filtered = self.filtering(grayscale)
        self.dprint("Bilateral filter", showResults)
        binarized = self.OtsuThresholding(filtered)
        #binarized = self.adaptiveThresholding(filtered)
        self.dprint("Otsu binarization", showResults)
        cleaned = self.cleanImage(binarized)
        self.dprint("Dilate-Erode", showResults)
        #rotated = self.skewCorrection(cleaned)
        self.saveImage(cleaned, dir+"/binarized_"+filename)
        #Template matching funcionando pero no integrado 
        #self.matchTemplate("../Images/Templates/DEVOTO_FM.jpg", cleaned)

        #self.dprint("Deskewed", showResults)
        #self.dsaveImage(rotated, "Deskewed.jpg", showResults)
        #corrected = self.perspectiveCorrection(rotated)
        #self.dprint("Dewarped", showResults)
        #self.dsaveImage(corrected, "Dewarped.jpg", showResults)
        # region = np.array([[0, self.height], [0, 0], [self.width, 0], [self.width, self.height]])
        # blank = np.zeros_like(cleaned)
        # boxRegion = cv.fillConvexPoly(blank, region, 255)
        # boxRegionImage = cv.bitwise_and(cleaned, boxRegion)
        # self.displayImage(boxRegionImage)
        # text = OCRFunctions.readRegionText(OCRFunctions, region, cleaned, "aa", True)
        # OCRFunctions.writeTextFile(OCRFunctions, text, "../Pruebas/wakawaka")
        # d = pytesseract.image_to_data(cleaned, output_type=Output.DICT)
        # n_boxes = len(d['level'])
        # boxes = cv.cvtColor(cleaned.copy(), cv.COLOR_BGR2RGB)
        # for i in range(n_boxes):
        #     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
        #     boxes = cv.rectangle(boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
        # self.plot_rgb(boxes)
        # plt.show()
        return cleaned

if __name__ == "__main__":
    preprocessing = imageFunctions("../Images/DEVOTO_FM/11.jpg", "DEVOTO_FM")
    resultImg = preprocessing.imagePreprocessing(preprocessing.img, True)