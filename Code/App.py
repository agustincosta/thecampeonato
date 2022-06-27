import img_funcs
import ocr_funcs
# import os
#import db_funcs

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

ocr_funcs.OCRFunctions.parseTextFile(ocr_funcs.OCRFunctions, 'DEVOTO/OCR_18')

# imagesDir = "../Images"
# for dirname in os.listdir(imagesDir):
#     imageFolder = dirname
    
#     if dirname == "Templates":
#         continue

#     for filename in os.listdir("../Images/"+imageFolder):
#         try:
#             print(imageFolder, localesDictionary[imageFolder], filename)
#             #preprocessing = img_funcs.imageFunctions("../Images/"+imageFolder+"/"+filename, localesDictionary[imageFolder])
#             #resultImg = preprocessing.imagePreprocessing(preprocessing.img, False, "../Results/"+imageFolder, filename)
#             #productRegion, priceRegion, completeImgRegion = preprocessing.textRegions(resultImg)

#             #productsText = ocr_funcs.OCRFunctions.readRegionText(ocr_funcs, productRegion, resultImg, 'Prod', True)
#             #ocr_funcs.OCRFunctions.writeTextFile(ocr_funcs, productsText, imageFolder+'/products'+filename)
#             #priceText = ocr_funcs.OCRFunctions.readRegionText(ocr_funcs, priceRegion, resultImg, 'Price', False)
#             #ocr_funcs.OCRFunctions.writeTextFile(ocr_funcs, priceText, imageFolder+'/price'+filename)
#             #completeText = ocr_funcs.OCRFunctions.readRegionText(ocr_funcs, completeImgRegion, resultImg, None, True)
#             #ocr_funcs.OCRFunctions.writeTextFile(ocr_funcs, completeText, imageFolder+'/OCR_'+filename)
#             file = filename.replace(".jpg","")
#             ocr_funcs.OCRFunctions.parseTextFile(ocr_funcs.OCRFunctions, imageFolder+'/OCR_'+file)
#         except Exception as e:
#             print(e)
#             continue
