import numpy as np
import psycopg2

startString = "Producto. "
endString = "Redondeo ."
enableWrite = False

try:
    conn =  psycopg2.connect(host="localhost",port="5432",database="factura_test",user="postgres",password="a250695postgres")
    print ("DB opened")

    mycursor = conn.cursor()

    mycursor.execute("select exists(select * from information_schema.tables where table_name=%s)", ('factura_macro',))
    
    if not mycursor.fetchone()[0]:
        mycursor.execute(
            """
            CREATE TABLE factura_macro(
                ID          SERIAL PRIMARY KEY,
                CODE        TEXT NOT NULL,
                DESCRIPTION TEXT NOT NULL,
                QUANTITY    TEXT NOT NULL,
                UNITPRICE   TEXT NOT NULL,
                TOTAL       TEXT NOT NULL
            );
            """
        )

except (Exception, psycopg2.DatabaseError) as error:
    print(error)

#finally:
        #if conn is not None:
        #    conn.close()



mylines = []                                # Declare an empty list named mylines.
mytextfile = ""
with open('text_result.txt','r', encoding="utf-8") as myfile: # Open lorem.txt for reading text data.
    for myline in myfile:                   # For each line, stored as myline,
        if not enableWrite:
            if startString in myline:
                enableWrite = True
        else:
            if endString in myline:
                break
            else:
                mylines.append(myline)              # add its contents to mylines.
                words = myline.split()
                if len(words) == 0:
                    continue
                code = words[0]
                quantity = words[len(words)-3]
                unitPrice = words[len(words)-2]
                total = words[len(words)-1]
                description = " "
                
                for i in range(1, len(words)-4):
                    description = description + " " + words[i]

                mycursor.execute("INSERT INTO factura_macro (CODE, DESCRIPTION, QUANTITY, UNITPRICE, TOTAL) VALUES (%s, %s, %s, %s, %s)", (code, description, quantity, unitPrice, total))

mycursor.close()
conn.commit()

with open('facturaTextCut.txt', 'w') as newfile:
    newfile.write(mytextfile.join(mylines))

myfile.close()
newfile.close()




"""
try:
    with mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysqldb.69",
        database="mydatabase"
    ) as connection:
        print(connection)
except mysql.connector.Error as e:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysqldb.69")
    mycursor = connection.cursor()
    mycursor.execute("CREATE DATABASE mydatabase")
    
mycursor = connection.cursor()
mycursor.execute("SHOW TABLES")

for x in mycursor:
  if x.
"""
