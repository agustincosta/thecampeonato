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
            self.dataset = np.loadtxt(file, dtype=str, delimiter=";")

    def getCloseMatches(self, word, numResults, cutoff):
        productsList = self.dataset[:,1]
        matches = difflib.get_close_matches(word, productsList, numResults, cutoff)
        indexes = []
        for m in matches:
            indexes.append(np.where(productsList == m))
        return matches, indexes

if __name__ == "__main__":
    cat = categorization("../Dataset/categorias.csv") 
    matches1, indexes1 = cat.getCloseMatches("AGUA", 3, 0.8) 
    matches2, indexes2 = cat.getCloseMatches("JANE", 3, 0.8)
    matches3, indexes3 = cat.getCloseMatches("LAVAR", 3, 0.8)
    print(matches1)
    print(indexes1) 
    print(matches2)
    print(indexes2)
    print(matches3)
    print(indexes3)