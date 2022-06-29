import cv2 as cv
import numpy as np
# import sys
# from PIL import Image
# from enum import Enum
import pytesseract
from difflib import SequenceMatcher
# import imutils
import db_funcs

class OCRFunctions:

    dbhandler = None

    def __init__(self):
        """Inicializacion de clase
        """        
        self.dbhandler = db_funcs.DBFunctions()

    def readRegionText(self, region, image, filename, includeLetters):
        """Hace OCR de una region de una imagen a partir de sus 4 esquinas

        Args:
            region (list): Esquinas del poligono
            image (image): Imagen objetivo
            filename (string): Nombre de archivo txt a escribir
            includeLetters (bool): Incluir o excluir letras de los posibles caracteres a leer

        Returns:
            text (string): Texto leido por OCR de la region
        """        
        blank = np.zeros_like(image)
        boxRegion = cv.fillConvexPoly(blank, region, 255)
        boxRegionImage = cv.bitwise_and(image, boxRegion)
        #cv.imshow(boxRegionImage)
        np.ones((3,3),np.uint8)
        # kernel = np.ones((3,3),np.uint8)
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
        """Verifica si una string puede ser convertida a float

        Args:
            value (string): String a verificar

        Returns:
            _ (bool): Es o no es float
        """        
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def insertProductDataToDb(self, text, tableName):    #No valido para TI o Macro
        """NO USAR - FUNCION VIEJA

        Args:
            text (_type_): _description_
            tableName (_type_): _description_

        Returns:
            _type_: _description_
        """        
        tableDefinition = "ID SERIAL PRIMARY KEY, Description TEXT NOT NULL, Units REAL NOT NULL, Price REAL NOT NULL"
        self.dbhandler.createTable(tableName, tableDefinition)
        lines = text.readlines()
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

    def compareLine(self, line, expression, thresh=0.95):
        """Intento previo de difflib.getCloseMatches. No utilizada

        Args:
            line (_type_): _description_
            expression (_type_): _description_
            thresh (float, optional): _description_. Defaults to 0.95.

        Returns:
            _type_: _description_
        """        
        FirstWord = False
        indx = 0 
        words = line.split()
        exp_words = expression.split()
        ratios = [0]*len(exp_words)

        if len(words) == 0:
            pass

        #Busca la primera palabra que coincida
        for j in range(0,len(words)-1):
            ratios[0] = SequenceMatcher(None, words[j], exp_words[0]).ratio()
            if (ratios[0] > thresh):
                indx = j
                FirstWord = True
                break
        
        #Compara las siguientes hasta encontrar la frase entera    
        if (len(exp_words) >= 2) and FirstWord:
            for i in range(1,len(exp_words)):
                ratios[i] = SequenceMatcher(None, words[indx+i], exp_words[i]).ratio()
        
        result = np.prod(ratios)

        return result

    def findSubstring(self, line: str, expression: str):
        result = line.find(expression)
        if result == -1:
            return False
        else:
            print(line + expression)
            return True

    def parseTextFile(self, textFile):
        """Lee archivo txt generado por OCR de factura buscando los limites de inicio y fin de zona de interes

        Args:
            textFile (str): Nombre del archivo .txt
        """        
        with open('../Results/'+textFile+'.txt', 'r') as txtFile:

            startFound = False
            while not startFound:
                line = txtFile.readline()
                if len(line) == 0:
                    break
                cf  = self.compareLine(self, line, "CONSUMO FINAL")
                moneda = self.compareLine(self, line, "MONEDA: UYU")
                if (cf > 0.9) or (moneda > 0.9):
                    startFound = True
                    print("START " + line)
                cf = 0
                moneda = 0
            endFound = False
            if startFound:
                while not endFound:
                    line = txtFile.readline()
                    if len(line) == 0:
                        break
                    print(line)
                    total  = self.compareLine(self, line, "TOTAL:")
                    tarjeta  = self.compareLine(self, line, "Tarjeta credito/debito")
                    efectivo  = self.compareLine(self, line, "Efectivo")
                    if (total > 0.9) or (tarjeta > 0.9) or (efectivo > 0.9):
                        endFound = True   
                        print("END: " + line)  
                    
                    #print(line)
                    
                    # if len(line) >= 25:
                    #     words = line.split()
                    #     print("Linea producto")
                    #     print(words)
                    #encontrar el precio y ponerlo en una columna, juntar lo demas
                    
        txtFile.close()    

    def priceTextConditioning(self, text):
        pass

    def writeTextFile(self, text:str, filename:str):
        """Escribe archivo de texto con OCR de foto

        Args:
            text (str): Texto a escribir
            filename (str): Nombre de foto 
        """        
        file = filename.replace(".jpg","")
        with open('../Results/'+file+'.txt', 'w') as txtFile:
            txtFile.write(text)
        txtFile.close()

if __name__ == "__main__":
    ocr = OCRFunctions()
    txtFile = 'DEVOTO/OCR_20'
    ocr.parseTextFile(txtFile)
    #with open('../Results/DEVOTO/OCR_18.txt', 'r') as txtFile:
        
        #print(ocr.insertProductDataToDb(txtFile, "test"))