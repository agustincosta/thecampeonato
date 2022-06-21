import difflib
from enum import unique
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
        """Inicializacion de clase. Lee dataset de CSV y guarda en array

        Args:
            filePath (string): ruta del archivo .csv
        """        
        self.dataset = []
        with open(filePath) as file:
            self.dataset = np.loadtxt(file, dtype=str, delimiter=",")

    def getCloseMatches(self, word, numResults, cutoff):
        """Obtiene los n resultados mas cercanos en dataset y el indice asociado

        Args:
            word (string): String contra la cual buscar matches
            numResults (int): Cantidad de resultados a devolver
            cutoff (float): 0 a 1, umbral para considerar match

        Returns:
            matches (list[string]): Lista de descripciones de productos en dataset que spn matches
            indexes (list[int]): Lista de indices en el dataset de estos matches
        """        
        productsList = self.dataset[:,1]
        matches = difflib.get_close_matches(word, productsList, numResults, cutoff)
        indexes = []
        for m in matches:
            indexes.append(np.where(productsList == m))
        return matches, indexes

    def selectMainCategory(self, categories):
        """Selecciona categoria principal a partir de las dadas

        Args:
            categories (list[string]): Lista de categorias matcheadas

        Returns:
            _ (string): Categoria principal
        """        
        try:
            return max(set(categories), key=categories.count)       
            # if (categories[0] == categories[1]):
            #     return categories[0]
            # elif (categories[0] == categories[2]):
            #     return categories[0]
            # elif (categories[1] == categories[2]):
            #     return categories[1]
            # else:
            #     return categories[0]
        except:
            if len(categories) == 0:
                return "OTROS"
            else:
                return categories[0]

    def addCategoriesTotal(self, categories, amounts):
        """Devuelve una lista con categorias unicas y los totales asociados

        Args:
            categories (list[string]): Lista de categorias para cada producto
            amounts (np.array[float]): Array de totales de cada producto

        Returns:
            uniqueCategories (list[string]): Lista de categorias unicas
            uniqueAmounts (np.array[float]): Array de totales para cada categoria unica
        """        
        uniqueCategories = []

        for cat in categories:
            if not (cat in uniqueCategories):
                uniqueCategories.append(cat)

        uniqueAmounts = np.zeros_like(uniqueCategories, dtype=float)
        i = 0

        for i in range(len(uniqueCategories)):
            for j in range(len(categories)):
                if (uniqueCategories[i] == categories[j]):
                    uniqueAmounts[i] = amounts[j] + uniqueAmounts[i]

        return uniqueCategories, uniqueAmounts    

    def categorizeItems(self, items, cutoff=0.9):
        """Categoriza la lista de productos a partir del dataset

        Args:
            items (list[string]): Lista de descripciones de productos
            cutoff (float, optional): Umbral para encontrar coincidencias. Defaults to 0.9.

        Returns:
            categorized (list[string]): Lista de categorias para cada producto
        """        
        productsList = self.dataset[:,1]
        categorized = []
        for item in items[0]:
            matches = difflib.get_close_matches(item, productsList, n=3, cutoff=cutoff)
            mainCategory = self.selectMainCategory(matches)
            index = np.where(productsList==mainCategory)

            if index == []:
                index = [1057]
            categorized.append(self.dataset[index,0][0][0])
        return categorized


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