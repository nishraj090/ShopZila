import sqlite3

# Open database
conn = sqlite3.connect('database.db')







conn.execute('''CREATE TABLE seller2(sId INTEGER PRIMARY KEY,seller_name TEXT,name1 TEXT,price1 REAL,description1 TEXT,image1 TEXT,stock1 INTEGER,categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId))''')

conn.execute('''CREATE TABLE featured1
		(productId INTEGER PRIMARY KEY,
		Seller_name TEXT,
		Product_name TEXT,
		price1 REAL,
		description1 TEXT,
		image1 TEXT,
		stock1 INTEGER,
		categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		)''')

conn.execute('''CREATE TABLE complaint2(C_ID INTEGER PRIMARY KEY,userId INTEGER,orderId INTEGER,description TEXT,feedback varchar(255),FOREIGN KEY(userId) REFERENCES users(userId),
FOREIGN KEY(orderId) REFERENCES order_ack(orderId))''')

conn.execute('''CREATE TABLE order_ack1(orderId INTEGER PRIMARY KEY,userId INTEGER,
		dt1 DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
		FOREIGN KEY(userId) REFERENCES users(userId)
		)''')"""

conn.execute('''CREATE TABLE fkart
		(userId INTEGER,
		productId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(featured1)
		)''')
conn.close()
