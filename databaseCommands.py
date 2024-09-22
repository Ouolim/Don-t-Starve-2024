import sqlite3
import time
import os

exists = os.path.isfile("data/database.db")
con = sqlite3.connect("data/database.db")
cur = con.cursor()

if not exists:
	print("IMPORTATNT! New database was created")
	cur.execute("CREATE TABLE codes(code, id, amount)")
	cur.execute("CREATE TABLE inventory(id, amount)")
	cur.execute("CREATE TABLE recipies(code, targetId, targetAmount, recepie, restriction)")
	cur.execute("CREATE TABLE usedCodes(code, id, amount, date)")
	con.commit()




def insertCode(code, id, amount):
	cur.execute("INSERT INTO codes VALUES(?, ?, ?)", (code, id, amount))
	con.commit()

def insertRecepie(code:str, targetId:int, targetAmount:int, recepie:str, restriction=None):
	cur.execute("INSERT INTO recipies VALUES(?, ?, ?, ?, ?)", (code, targetId, targetAmount, recepie, restriction))
	con.commit()

def codeExist(code, database = 0):
	if database == 0:
		cur.execute("SELECT * FROM codes WHERE code = ?", (code,))
	else:
		cur.execute("SELECT * FROM usedCodes WHERE code = ?", (code,))
	row = cur.fetchone()
	return row if row != None else None

def useCode(code):
	cur.execute("SELECT * FROM codes WHERE code = ?", (code,))
	row = cur.fetchone()
	if row is None:
		return False
	cur.execute("DELETE FROM codes WHERE code = ?", (code,))
	cur.execute("INSERT INTO usedCodes VALUES(?, ?, ?, ?)", (code, row[1], row[2], time.time()))
	con.commit()
	return True

def readRecepie(code):
	cur.execute("SELECT * FROM recipies WHERE code = ?", (code,))
	row = cur.fetchone()
	return row if row != None else None
def fetchInventory():
	cur.execute("SELECT * FROM inventory")
	row = cur.fetchall()

	inventory = {}
	for id, amount in row:
		inventory[id] = amount

	return inventory
def insertInventory(id, delta):
	cur.execute("SELECT * FROM inventory where id = ?", (id,))
	row = cur.fetchone()
	if row is None:
		if delta <= 0:
			return False
		cur.execute("INSERT INTO inventory VALUES(?, ?)", (id, delta))
	else:
		cur.execute("UPDATE inventory SET amount = ? WHERE id = ?", (row[1] + delta, id))
	con.commit()
	return True

def fetchRecepies():
	cur.execute("SELECT * FROM recipies")
	row = cur.fetchall()
	return row

def removeRecepie(code):
	cur.execute("DELETE FROM recipies WHERE code = ?", (code,))
	con.commit()

if __name__ == "__main__":
	pass

