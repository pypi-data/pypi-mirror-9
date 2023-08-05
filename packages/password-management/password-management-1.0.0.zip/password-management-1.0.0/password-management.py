#!/usr/bin/python
#password and message app
#steven snowball

import os
import sqlite3
import random

##############################################################################################################
##### database defs
##############################################################################################################

def database_connect():
	#create / connnect to database
	#make the variable global so can throughout program
	global conn 
	#connects to database file
	conn = sqlite3.connect("pass.db")
	
	#make the variable global so can throughout program
	global cursor
	#moves the database connection into variable
	cursor = conn.cursor()
	

def database_disconnect():
	#disconnect database
	conn.close()


def table_create():
	#connnect to database
	database_connect()

	#create user table
	cursor.execute("""CREATE TABLE users
	                  (user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	                  	user_name VARCHAR NOT NULL,
	                  	user_password VARCHAR NOT NULL,
	                  	user_active BOOLEAN NOT NULL)
	               """)
	print("user table created")

	#create password table
	cursor.execute("""CREATE TABLE passwords
	                  (pass_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	                  	pass_user INTEGER NOT NULL,
	                  	password VARCHAR NOT NULL,
	                  	pass_program VARCHAR NOT NULL,
	                  	pass_active BOOLEAN NOT NULL)
	               """)
	print("password table created")


	
	#disconnect from database
	database_disconnect()



##############################################################################################################
##### user defs
##############################################################################################################

def user_table_select(type):
	#connnect to database
	database_connect()

	#use variable type to run different select statements
	if type == "check":
		#type check is to see if user exists in database
		cursor.execute("SELECT user_id FROM users WHERE user_name=? AND user_password=? AND user_active=?", (user_name, user_password,True))
		#put the length of the results into a variable
		result = len(cursor.fetchall())

		#use variable to see if select statement returned anything
		if result == 0:
			#no user
			output = False
		else:
			#user exists
			output = True 

		#disconnect from database
		database_disconnect()
		
		#return true/false as if user in in database
		return output
	
	elif type == "info":
		#select user id from database
		cursor.execute("SELECT user_id FROM users WHERE user_name=? AND user_password=? AND user_active=?", (user_name, user_password,True))
		#put results into a variable
		rows = cursor.fetchall()

		#make user id a global variable to use throughout program
		global u_id
		#for statement that loops around returning the user id and assigning it to a variable (should always just be 1 result)
		for row in rows:
			u_id = row[0]

		#disconnect from database
		database_disconnect()
		
	else:
		#tyoe variable doesn't match what we want so error
		print("error with code - please contact creator")

		#disconnect from database
		database_disconnect()
		
		#as error program quits as code not working
		exit()

def user_table_insert():
	#connnect to database
	database_connect()

	#inserts users into table
	cursor.execute("INSERT INTO users (user_name, user_password, user_active) VALUES (?,?,?);", (user_name, user_password,True))
	conn.commit()

	#checks to see if user what inserted into database
	if user_table_select("check") == True:
		#user what created
		print("user created")
		#user has been created run get into for the user id
		user_table_select("info")
		
		#return the users name
		print("hello ", user_name, "\n")
	else:
		#user was for some reason not created
		print("user not created")
		#re-run user setup
		user_setup()

	#disconnect from database
	database_disconnect()


##############################################################################################################
##### password defs
##############################################################################################################

def password_select(type, password_check):
	#connect to database
	database_connect()

	if type == "check":
		#select to see if table is there
		cursor.execute("SELECT * FROM passwords WHERE pass_user=? AND pass_active=?", (u_id, True))
		#print(cursor.fetchall())
		result = len(cursor.fetchall())
	elif type == "one":
		#select to see if password is there
		cursor.execute("SELECT pass_id FROM passwords WHERE password=? AND pass_user=? AND pass_active=?", (password_check, u_id, True))
		#print(cursor.fetchall())
		result = len(cursor.fetchall())
	elif type == "all":
		#select to see if password is there
		print(u_id)
		cursor.execute("SELECT * FROM passwords WHERE pass_user=? AND pass_active=?", (u_id, True))
		result = 1
		rows = cursor.fetchall()
	
		for row in rows:
			print(row)

		print("\n")

	else:
		print("error")


	if result == 0:
		output = False #no passwords
	else:
		output = True #passwords

	#disconnect from database
	database_disconnect()
	
	return output


def password_insert():
	#connect to database
	database_connect()

	program = input("what program is the password for? \t")
	control1 = input("choose 1.enter own, 2.generate password or r to return \t")

	if control1 == "1":
		password = input("what is the password? \t")

	elif control1 == "2":
		#password generator
		password = password_create()
		
	elif control1 == "r":
		password_management()

	else:
		print("error")
		password_management()

	#inserts password into table
	cursor.execute("INSERT INTO passwords (pass_user, password, pass_program, pass_active) VALUES (?,?,?,?);", (u_id, password, program, True))
	conn.commit()

	if password_select("one", password) == True:
		print("password created")
	else:
		print("password not created")

	#disconnect from database
	database_disconnect()



def password_delete():

	password_select("all","n")

	#connect to database
	database_connect()

	chooser = input("choose number of password above to delete \t")

	#deletes password in table
	cursor.execute("DELETE * FROM passwords WHERE pass_id=?", (chooser,))
	conn.commit()

	print("password deleted")

	#disconnect database
	database_disconnect()

	password_management()



def password_create():
	pass_len = input("how long do you want your password to be? \t")
	pass_type = input("what type of password do you want? 1.simple, 2.medium, 3.complex \t")
	c_password = ""

	s_list = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')
	m_list = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9')
	c_list = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9',']','[','?','<','~','#','!','@','$','%','^','&','*','(',')','+','}','|',':',';','>','{')

	
	for num in range(int(pass_len)):
		rand1 = random.randint(1,10)

		if pass_type == "1":
			p_option = s_list
			rand2 = random.randint(0,int(len(s_list)))
		elif pass_type == "2":
			p_option = m_list
			rand2 = random.randint(0,int(len(m_list)))
		elif pass_type == "3":
			p_option = c_list
			rand2 = random.randint(0,int(len(c_list)))
		else:
			print("error")

		if rand1 < 5:
			c_password += p_option[rand2].upper()
		else:
			c_password += p_option[rand2].lower()

	print(c_password)
	return c_password


##############################################################################################################
##### controls defs
##############################################################################################################

def database_setup():
	#scheck if database exists if not create it
	file_name = "passwords.db"
	if os.path.exists(file_name) == False: 
		print("database needs creating")
		table_create()
		print("database created")
	else:
		print("database exists")


def user_setup():
	#make user variables global
	global user_name
	global user_password

	#make sure variables are blank
	user_name = ""
	user_password = ""

	#get variables for the user information
	user_name = input("What is your user_name? \t")
	user_password = input("what is your password? \t")

	#run database set up
	database_setup()

	#check to see if user exists in not create it
	if user_table_select("check") == True:
		#user exists
		print("user exists")
		#get user id from database
		user_table_select("info")
		#return the users name
		print("hello ", user_name, "\n")
	else:
		#user doesn't exist needs creating
		print("user doesnt exist")
		#insert new user into database
		user_table_insert()


def password_management():
	
	control = input("choose 1.view, 2.add, 3.delete or q to quit \t")

	if control == "1":
		#view passwords
		if password_select("check","n") == True:
			password_select("all","n")
		else:
			print("no passwords")

		password_management()

	elif control == "2":
		#add passwords
		password_insert()
		password_management()

	elif control == "3":
		#delete password
		print("delete password")
		password_delete()
		password_management()

	elif control == "q":
		quit()
	else:
		#error
		print("error choose 1,2,3")
		password_management()


def options():
	option = input("choose either 1.passwords or q to quit \t")

	if option == "1":
		password_management()
	elif option.upper() == "Q":
		quit()
	else:
		print("you did not choose a correct option \n")
		options()



##############################################################################################################
##### program
##############################################################################################################

print("\t\t Welcome to Password App \n")

user_setup()
options()

