from flask import Flask, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_USER'] = 'sql3140347'
app.config['MYSQL_PASSWORD'] = '8Sy9VubZKL'
app.config['MYSQL_DB'] = 'sql3140347'
app.config['MYSQL_HOST'] = 'sql3.freemysqlhosting.net'

mysql = MySQL(app)


@app.route('/')
def users():
    cur = mysql.connection.cursor() #connects to database and gets cursor
    cur.execute('''SELECT Discoverable FROM Users''') #runs query
    rv = cur.fetchall() #return value 
    return str(rv)

@app.route('/discoverable', methods=['POST'])
def discoverable(): #WHICH EMAIL 
	email = request.form['email']
	insert = request.form['status'] 

	cur = mysql.connection.cursor()
	cur.execute('''SELECT Discoverable FROM Users''')

	if insert == 'on':
		cur.execute('''UPDATE Users SET Discoverable = True WHERE email = (%s)''', (email,))
	elif insert == 'off':
		cur.execute('''UPDATE Users SET Discoverable = False WHERE email = (%s)''', (email,))
    	#ADD HERE

	mysql.connection.commit()
	return "Done"

if __name__ == '__main__':
    app.run(debug=True)