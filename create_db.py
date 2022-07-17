#this file run once time to create database, after first use we can delete it
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", passwd="Lytvynyuk87")

my_cursor = mydb.cursor()

#my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)