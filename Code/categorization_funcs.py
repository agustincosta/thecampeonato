import difflib
import numpy as np

class categorization:

    categories = ["BEBIDAS",
                "PANADERIA",
                "LACTEOS",
                "CARNES Y FIAMBRES",
                "CONGELADOS",
                "FRUTAS Y VERDURAS",
                "ALIMENTOS PREPARADOS",
                "ALMACEN",
                "COPETIN",
                "DULCES Y POSTRES",
                "LIMPIEZA",
                "BAÑO",
                "HIGIENE PERSONAL",
                "COCINA",
                "ELECTRODOMESTICOS",
                "PAPELERIA",
                "TEXTILES",
                "FERRETERIA",
                "DEPORTES Y FITNESS"]

    path = "../Dataset/categorias.csv"

    def __init__(self, filePath):
        self.dataset = []
        with open(filePath) as file:
            self.dataset = np.loadtxt(file, delimiter=";")

    def getCloseMatches(self, word, numResults, cutoff):
        difflib.get_close_matches(word, self.dataset[:,1], numResults, cutoff)