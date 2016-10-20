from flask import Flask, request
from flask_mysqldb import MySQL

# set up flask app
app = Flask(__name__)

# configuration
app.config['MYSQL_USER'] = 'sql3140347'
app.config['MYSQL_PASSWORD'] = '8Sy9VubZKL'
app.config['MYSQL_DB'] = 'sql3140347'
app.config['MYSQL_HOST'] = 'sql3.freemysqlhosting.net'

# set up mysql database
mysql = MySQL(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/register', methods=['POST'])
def register_route():
    """Register user into database"""
    email = request.form['email']
    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO Users (Email) VALUES (%s)''', (email,))
    mysql.connection.commit()
    return "Done"

@app.route('/location', methods=['POST'])
def location(): 
    """Update location (latitude/longitude) of given user"""
    email = request.form['email']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    cur = mysql.connection.cursor()
    
    cur.execute('''UPDATE Users SET Latitude = %s WHERE email = (%s)''', (latitude,email,))
    cur.execute('''UPDATE Users SET Longitude = %s WHERE email = (%s)''', (longitude,email,))

    mysql.connection.commit()
    return "Done"

@app.route('/discoverable', methods=['POST'])
def discoverable(): 
    """Update "discoverable" boolean"""
    email = request.form['email']
    nsert = request.form['status']

    cur = mysql.connection.cursor()

    if insert == 'on':
        cur.execute('''UPDATE Users SET Discoverable = True WHERE email = (%s)''', (email,))
    elif insert == 'off':
        cur.execute('''UPDATE Users SET Discoverable = False WHERE email = (%s)''', (email,))

    mysql.connection.commit()
    return "Done"

@app.route('/api/user')
def user_route():
    """Fetches all users"""
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Users''')
    rv = cursor.fetchall()
    return str(rv)

if __name__ == '__main__':
    app.run(debug=True)
