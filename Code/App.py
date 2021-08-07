import img_funcs
import ocr_funcs
#import db_funcs

preprocessing = img_funcs.imageFunctions("../Images/DISCO_FM/1.jpg", img_funcs.locales.Disco)
CFBoxFound, cleanedImg = preprocessing.imageConditioning()
productRegion, priceRegion = preprocessing.textRegions(cleanedImg)
productsText = ocr_funcs.OCRFunctions.readRegionText(ocr_funcs, productRegion, cleanedImg, 'Prod')
ocr_funcs.OCRFunctions.writeTextFile(ocr_funcs, productsText, 'productsText')
priceText = ocr_funcs.OCRFunctions.readRegionText(ocr_funcs, priceRegion, cleanedImg, 'Price')
ocr_funcs.OCRFunctions.writeTextFile(ocr_funcs, priceText, 'priceText')