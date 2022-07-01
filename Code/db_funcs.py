# from ast import If
import numpy as np
import psycopg2
#import pandas
import matplotlib.pyplot as plt
#from sqlalchemy import create_engine
import categorization_funcs
# import datetime
import csv

class DBFunctions:
    cursor = None
    conn = None
    dbname = ""

    def __init__(self, dbname="expense_tracking", hostname="localhost", portno="5432", usr="postgres", pwd="a250695postgres"):
        """Inicializacion de clase. Genera conexion con DB y obtiene cursor

        Args:
            dbname (str, optional): Nombre de DB. Defaults to "expense_tracking".
            hostname (str, optional): Hostname. Defaults to "localhost".
            portno (str, optional): Numero de puerto. Defaults to "5432".
            usr (str, optional): Username. Defaults to "postgres".
            pwd (str, optional): Password. Defaults to "a250695postgres".
        """        
        try:
            self.conn = psycopg2.connect(host=hostname, port=portno, database=dbname, user=usr, password=pwd)
            self.cursor = self.conn.cursor()
            self.dbname = dbname
        except (Exception, psycopg2.Error, psycopg2.DatabaseError) as e:
            print(e)

    def createTable(self, tableName, definition):
        """Crea nueva tabla en db

        Args:
            tableName (string): Nombre de tabla
            definition (string): Opciones (columnas, pk, etc)
        """        
        try:
            self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (tableName,))
            if not self.cursor.fetchone()[0]:
                self.cursor.execute("CREATE TABLE " + tableName + " ( " + definition + " ) ")
                print("Table created")
            else:
                self.cursor.execute("TRUNCATE TABLE " + tableName)
                print("Table exists already")
            self.commitChanges()
        except (Exception, psycopg2.Error, psycopg2.DatabaseError) as e:
            print(e)

    def insertProductLine(self, tableName, description, units, price):
        """Inserta una linea de producto en la tabla de detalles en la DB

        Args:
            tableName (string): Nombre de la tabla
            description (string): Descripcion del producto
            units (float): Unidades del producto
            price (float): Precio unitario del producto
        """        
        try:
            self.cursor.execute("INSERT INTO " + tableName + " (Description, Units, Price) VALUES (%s, %s, %s)", (description, str(units), str(price)))
        except (Exception, psycopg2.Error, psycopg2.DatabaseError) as e:
            print(e)

    def commitChanges(self):
        """Hace efectivos cambios en DB
        """        
        self.conn.commit()

    def getSinglePurchaseInfo(self, purchase_id):
        """Devuelve informacion de una unica compra por purchase_id

        Args:
            purchase_id (int): ID de compra

        Returns:
            _: lista con purchase_id, user_id, store_id, timestamp y total
        """        
        select_query = ("SELECT * FROM general_table WHERE purchase_id = " + purchase_id)
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def getUserPurchaseInfo(self, user_id):
        """Devuelve informacion de todas las compras hechas por un usuario

        Args:
            user_id (int): ID de usuario

        Returns:
            _: lista de listas con purchase_id, user_id, store_id, timestamp y total por cada compra
        """        
        select_query = "SELECT * FROM general_table WHERE user_id = " + user_id
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def uniquePurchaseAnalysis(self, labels, amounts, user_id, purchase_date, purchase_id, plot=False):  
        """Categorizacion de compra (unica) y pie chart opcional

        Args:
            labels (list[string]): Lista de descripciones de productos
            amounts (np.array[float]): Array con los precios de cada producto
            user_id (int): ID de usuario para query en users_table
            purchase_date (datetime): Fecha de la compra formato datetime
            purchase_id (int): ID de compra para querys en multiples tablas
            plot (bool, optional): Graficar el resultado de la categorizacion. Defaults to False.

        Returns:
            uniqueCats (list[string]): Lista de las categorias 
            uniqueAmts (np.array[float]): Array de total para cada categoria
        """          
        cat = categorization_funcs.Categorization("../Dataset/categorias.csv")
        categories = cat.categorizeItems(labels, cutoff=0.4)
        uniqueCats, uniqueAmts = cat.addCategoriesTotal(categories, amounts)

        select_query = "SELECT * FROM processed_purchases_table ORDER BY id DESC"
        self.cursor.execute(select_query)
        data = self.cursor.fetchone()

        if self.cursor.rowcount == 0:
            current_pk_id = 0
        else:
            current_pk_id = data[0,0] + 1

        select_query = "SELECT * FROM processed_purchases_table WHERE purchase_id = " + purchase_id
        self.cursor.execute(select_query)
        data = self.cursor.fetchall()

        if self.cursor.rowcount == 0:
            for i in range (len(amounts)):
                current_pk_id = current_pk_id + i
                insert_query = "INSERT INTO processed_purchases_table VALUES (" + str(current_pk_id) + "," + str(purchase_id) + "," + str(uniqueCats[i]) + "," + str(uniqueAmts[i]) + "," + str(user_id) + "," + str(purchase_date) + ")"
                self.cursor.execute(insert_query)
        
        self.commitChanges()

        select_query = ("SELECT * FROM users_table WHERE user_id = " + str(user_id))
        self.cursor.execute(select_query)
        users_data = np.array(self.cursor.fetchall())

        user_name = users_data[0,1]

        if plot:
            fig1, ax1 = plt.subplots()
            ax1.pie(uniqueAmts, labels=uniqueCats, autopct='%1.1f%%', shadow=False, startangle=90)
            ax1.axis('equal')
            plt.title('Compra de ' + user_name + ' el día ' + purchase_date.strftime("%d %b %Y"))
            plt.show()

        return uniqueCats, uniqueAmts

    def getLastPurchases(self, n=5):
        """Devuelve el ID de las ultimas n compras

        Args:
            n (int, optional): Cantidad de compras que devolver. Defaults to 5.

        Returns:
            pid (np.array[int]): Array con los purchase_id 
        """        
        select_query = "SELECT purchase_id FROM general_table ORDER BY timestamp DESC"
        self.cursor.execute(select_query)
        pid = np.zeros(n, dtype=int)
        for i in range (n):
            pid[i] = int(self.cursor.fetchone()[0])
        return pid

    def getUsersInGroup(self, group_nr):
        """Devuelve los user_id pertenecientes al grupo

        Args:
            group_nr (int): Numero de grupo

        Returns:
            group_users_id (np.array[int]): Array con los user_id
        """        
        select_query = ("SELECT user_id FROM users_table WHERE group_member = " + str(group_nr))
        self.cursor.execute(select_query)
        group_users_id = np.array(self.cursor.fetchall())
        return group_users_id

    def getUserMonthlyPurchases(self, user_id, month, year):
        """Devuelve los detalles de las compras realizadas por un usuario en un mes y año dados

        Args:
            user_id (int): ID de usuario
            month (int): Mes de compras
            year (int): Año de compras

        Returns:
            uniqueMthlyAmts (np.array[float]): Array con las cantidades para cada categoria unica
            uniqueMthlyCats (list[string]): Lista con las categorias unicas para el mes
            user_mthly_prods (list[string]): Lista con las descripciones de todos los productos del mes
            categories (list[string]): Lista de categorias para cada producto del mes
            RecordFound (bool): Indica si existen compras para ese user para el mes
        """        
        select_query = ("SELECT * FROM general_table WHERE user_id = " + str(user_id) + " AND (timestamp BETWEEN '" + str(year) + "-" + str(month) + "-1' AND '" + str(year) + "-" + str(month) + "-31')")
        self.cursor.execute(select_query)
        user_mthly_general = np.array(self.cursor.fetchall())

        if self.cursor.rowcount != 0:
            user_mthly_pids = user_mthly_general[:,0]

            user_mthly_labels = []
            user_mthly_prods = []
            user_mthly_amts = np.zeros(1)

            for i in range(len(user_mthly_pids)):
                select_query = ("SELECT * FROM details_table WHERE purchase_number = " + str(user_mthly_pids[i]))
                self.cursor.execute(select_query)
                purchase_detail = np.array(self.cursor.fetchall())

                user_mthly_labels.append(purchase_detail[:,2])
                user_mthly_prods.append(purchase_detail[:,2])
                user_mthly_amts = np.append(user_mthly_amts, purchase_detail[:,5])
    

            uniqueMthlyCats, uniqueMthlyAmts = self.purchaseAnalysis(user_mthly_labels, user_mthly_amts, user_id, purchase_date="5/2022", purchase_id=1)

            cat = categorization_funcs.Categorization("../Dataset/categorias.csv")
            categories = cat.categorizeItems(user_mthly_labels, cutoff=0.4)    
            uniqueMthlyCats, uniqueMthlyAmts = cat.addCategoriesTotal(categories, user_mthly_amts)

            select_query = ("SELECT * FROM users_table WHERE user_id = " + str(user_id))
            self.cursor.execute(select_query)
            users_data = np.array(self.cursor.fetchall())

            user_name = users_data[0,1]

            titulo = 'Desglose mensual de ' + user_name + ' del mes ' + str(month) + '/' + str(year)
            self.plotPieChart(uniqueMthlyAmts, uniqueMthlyCats, titulo)

            RecordFound = True

        else:
            uniqueMthlyAmts = np.array([])
            uniqueMthlyCats = []
            user_mthly_prods = []
            categories = []
            RecordFound = False

        return uniqueMthlyAmts, uniqueMthlyCats, user_mthly_prods, categories, RecordFound

    def getGroupMonthlyPurchases(self, group_id, month, year, checkCategorization=False):
        """Obtiene las compras para un mes dado para un grupo de usuarios

        Args:
            group_id (int): ID del grupo
            month (int): Mes de las compras
            year (int): Año de las compras
            checkCategorization (bool, optional): Generar csv con los productos y sus categorias para debug. Defaults to False.

        Returns:
            uniqueGroupMthlyAmts (np.array[float]): Array de totales para cada categoria unica del mes para grupo
            uniqueGroupMthlyCategories (list[string]): Lista de categorias unicas del mes para grupo
        """        
        users_in_group = self.getUsersInGroup(group_id)

        group_mthly_labels = []
        user_mthly_labels = []
        group_mthly_prods = []
        user_mthly_prods = []
        user_categories = []
        group_categories = []
        group_mthly_amts = np.empty(1, dtype=float)
        user_mthly_amts = np.empty(1, dtype=float)

        for user in users_in_group:
            user_mthly_amts, user_mthly_labels, user_mthly_prods, user_categories, record_found = self.getUserMonthlyPurchases(user[0], month=month, year=year)
            if record_found:
                group_mthly_labels.extend(user_mthly_labels)
                if user==users_in_group[0]:
                    group_mthly_amts = user_mthly_amts
                else:
                    group_mthly_amts = np.append(group_mthly_amts, user_mthly_amts)
                if checkCategorization:
                    group_mthly_prods.extend(user_mthly_prods[0])
                    group_categories.extend(user_categories)

        cat = categorization_funcs.Categorization("../Dataset/categorias.csv")
        uniqueGroupMthlyCategories, uniqueGroupMthlyAmts = cat.addCategoriesTotal(group_mthly_labels, group_mthly_amts)

        titulo = 'Desglose mensual de grupo ' + str(group_id) + ' del mes ' + str(month) + '/' + str(year)
        self.plotPieChart(uniqueGroupMthlyAmts, uniqueGroupMthlyCategories, titulo)

        if checkCategorization:
            
            with open('categorization.csv', 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                for i in range(len(group_categories)):
                    data = [group_categories[i], group_mthly_prods[i]]
                    writer.writerow(data)

        return uniqueGroupMthlyAmts, uniqueGroupMthlyCategories


    def plotPieChart(self, amounts, categories, plotTitle):
        """Grafica pie chart de categorias acorde a totales

        Args:
            amounts (np.array[float]): Array de totales
            categories (list[string]): Lista de categorias
            plotTitle (string): Titulo
        """        
        fig1, ax1 = plt.subplots()
        exp = np.ones_like(amounts)/50
        ax1.pie(amounts, labels=categories, autopct='%1.1f%%', shadow=False, startangle=90, explode=exp)
        ax1.axis('equal')
        plt.title(plotTitle, y=1.08)
        plt.show()

    def closeConnection(self):
        """Cierra la conexion con DB y hace efectivos los cambios
        """        
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

if __name__ == '__main__':
    db = DBFunctions()
    db.getGroupMonthlyPurchases(2, 5, 2021, True)