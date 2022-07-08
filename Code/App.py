import img_funcs
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

if len(sys.argv) < 2:
    raise Exception("Insufficient parameters")

try:
    imagePath = sys.argv[1]         #with filename and extension

    preprocessing = img_funcs.ImageFunctions(imagePath)
    result_text = preprocessing.readImageText()
    print(result_text)
except Exception as e:
    print(e)

