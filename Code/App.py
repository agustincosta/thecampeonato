import img_funcs
import ocr_funcs
import os
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

imagesDir = "../Images"
for dirname in os.listdir(imagesDir):
    imageFolder = dirname
    
    if dirname == "Templates":
        continue

    for filename in os.listdir("../Images/"+imageFolder):
        try:
            print(imageFolder, localesDictionary[imageFolder], filename)
            preprocessing = img_funcs.imageFunctions("../Images/"+imageFolder+"/"+filename, localesDictionary[imageFolder])
            CFBoxFound, cleanedImg = preprocessing.imageConditioning("../Results/"+imageFolder, filename)
            productRegion, priceRegion = preprocessing.textRegions(cleanedImg)

            productsText = ocr_funcs.OCRFunctions.readRegionText(ocr_funcs, productRegion, cleanedImg, 'Prod', True)
            ocr_funcs.OCRFunctions.writeTextFile(ocr_funcs, productsText, imageFolder+'/products'+filename)
            priceText = ocr_funcs.OCRFunctions.readRegionText(ocr_funcs, priceRegion, cleanedImg, 'Price', False)
            ocr_funcs.OCRFunctions.writeTextFile(ocr_funcs, priceText, imageFolder+'/price'+filename)
        except Exception as e:
            print(e)
            continue
