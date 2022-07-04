from unittest import result
import img_funcs
import ocr_funcs
import sys

localesDictionary = {"DEVOTO" : img_funcs.locales.Devoto,
                     "DEVOTO_FM" : img_funcs.locales.Devoto,
                     "DISCO_FM" : img_funcs.locales.Disco,
                     "FROG" : img_funcs.locales.Frog,
                     "GEANT" : img_funcs.locales.Geant,
                     "KINKO" : img_funcs.locales.Kinko,
                     "MACRO" : img_funcs.locales.Macro,
                     "TATA" : img_funcs.locales.Tata,
                     "TI" : img_funcs.locales.TiendaInglesa
}

if len(sys.argv) < 4:
    raise Exception("Unsufficient parameters")

try:
    imagePath = sys.argv[1]         #with filename and extension
    resultPath = sys.argv[2]        #just result directory path
    resultFilename = sys.argv[3]    #filename without extension

    preprocessing = img_funcs.imageFunctions(imagePath)
    resultImg = preprocessing.imagePreprocessing(preprocessing.img, False, resultPath, resultFilename)
    productRegion, priceRegion, completeImgRegion = preprocessing.textRegions(resultImg)

    ocr = ocr_funcs.OCRFunctions
    result_text = ocr.readRegionText(ocr, completeImgRegion, resultImg, None, True)
    ocr.writeTextFile(ocr, result_text, resultPath + 'OCR_'+resultFilename)
except Exception as e:
    print(e)

