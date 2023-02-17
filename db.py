import sqlite3

conn = sqlite3.connect('transactions.db')
c = conn.cursor()

c.execute('''CREATE TABLE transactions 
             (id INTEGER PRIMARY KEY, 
             business_facility TEXT, 
             date DATE, 
             emissions INTEGER)''')

# Insert some sample data
c.execute("INSERT INTO transactions (business_facility, date, emissions) VALUES (?, ?, ?)", ("GreenEatChangi", "2021-01-01", 1.23))
c.execute("INSERT INTO transactions (business_facility, date, emissions) VALUES (?, ?, ?)", ("GreenEatOrchard", "2021-01-01", 2.34))
c.execute("INSERT INTO transactions (business_facility, date, emissions) VALUES (?, ?, ?)", ("GreenEatChangi", "2021-02-01", 3.45))
c.execute("INSERT INTO transactions (business_facility, date, emissions) VALUES (?, ?, ?)", ("GreenEatOrchard", "2021-02-01", 4.56))

conn.commit()
conn.close()
