import cv2 as cv
import numpy as np
import sys
from PIL import Image
from enum import Enum
import pytesseract
from difflib import SequenceMatcher
import imutils
import db_funcs

class OCRFunctions:

    dbhandler = None

    def __init__(self):
        self.dbhandler = db_funcs.DBFunctions()

    def readRegionText(self, region, image, filename, includeLetters):
        blank = np.zeros_like(image)
        boxRegion = cv.fillConvexPoly(blank, region, 255)
        boxRegionImage = cv.bitwise_and(image, boxRegion)
        #cv.imshow(boxRegionImage)
        kernel = np.ones((3,3),np.uint8)
        #boxRegionImage = cv.dilate(boxRegionImage, kernel, None, iterations=1)
        if not (filename == None):
            cv.imwrite('text' + filename + '.jpg', boxRegionImage)
        ocr_options_text = '--psm 3 -c preserve_interword_spaces=1 -c tessedit_char_whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$-+:.,!/()*[] " load_system_dawg=false load_freq_dawg=false'
        ocr_options_nums = '--psm 3 -c preserve_interword_spaces=1 -c tessedit_char_whitelist="0123456789$-+:., " load_system_dawg=false load_freq_dawg=false'
        if includeLetters:
            ocr_options = ocr_options_text
        else:
            ocr_options = ocr_options_nums
        text = pytesseract.image_to_string(boxRegionImage, lang="spa", config=ocr_options)
        #text = pytesseract.image_to_data(boxRegionImage, lang="spa", config=ocr_options)
        return text
    
    def isfloat(self, value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def insertProductDataToDb(self, text, tableName):    #No valido para TI o Macro
        tableDefinition = "ID SERIAL PRIMARY KEY, Description TEXT NOT NULL, Units REAL NOT NULL, Price REAL NOT NULL"
        self.dbhandler.createTable(tableName, tableDefinition)
        lines = text.readlines()
        prevLine = ""
        prevWords = []
        for line in lines:                  #Leo linea por linea
            if lines == "\n":
                continue
            line.replace(",",".")           #Si los numeros tienen coma no cuentan como float
            words = line.split()            #Separo lineas en palabras
            if len(words) < 4:
                continue
            
            if (self.isfloat(words[0]) and words[1]=='UN' and words[2]=='x' and self.isfloat(words[3])):
                self.dbhandler.insertLine(tableName, prevWords, float(words[0]), float(words[3]))
                            
            prevWords = words
        self.dbhandler.cursor.execute("SELECT * FROM public." + tableName + " ORDER BY ID ASC")
        output = self.dbhandler.cursor.fetchall()

        self.dbhandler.commitChanges()
        self.dbhandler.closeConnection()
        return output

    def priceTextConditioning(self, text):
        pass

    def writeTextFile(self, text, filename):
        with open('../Results/'+filename+'.txt', 'w') as txtFile:
            txtFile.write(text)
        txtFile.close()

if __name__ == "__main__":
    ocr = OCRFunctions()
    with open('../Results/DEVOTO/products4.jpg.txt', 'r') as txtFile:
        print(ocr.insertProductDataToDb(txtFile, "test"))