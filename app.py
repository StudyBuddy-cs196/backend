from flask import Flask, request
from flask_mysqldb import MySQL
import webscraper

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

@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if (request.method == 'GET'):
        pass
    elif (request.method == 'POST'):
        email = request.form['email']
        add = request.form['status']
        course = request.form['course']
        cur = mysql.connection.cursor()

        if add == "True": #add a course
            cur.execute('''INSERT INTO UsersAndCourses (Email, CourseCode) VALUES (%s, %s)''', (email,course))
        elif add == "False": #drop a course
            cur.execute('''DELETE FROM UsersAndCourses WHERE Email = (%s) AND CourseCode = (%s)''', (email,course))

    mysql.connection.commit()
    return "Done"

@app.route('/matches', methods=['GET'])
def matches(): 
    #include parameter for course search
    course = request.args.get('course')

    #find people who are studying same course (can't return same person)

    #find people in database who are discoverable
    cur = mysql.connection.cursor()
    cur.execute('''SELECT Email FROM Users WHERE Discoverable = True''')
    people = cur.fetchall()
    
    #rank people based on location 
    
    #return array of people as JSON file

@app.route('/location', methods=['POST'])
def location():
    """Update location (latitude/longitude) of given user"""
    email = request.form['email']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    cur = mysql.connection.cursor()

    cur.execute('''UPDATE Users SET Latitude = %s WHERE Email = (%s)''', (latitude,email,))
    cur.execute('''UPDATE Users SET Longitude = %s WHERE Email = (%s)''', (longitude,email,))

    mysql.connection.commit()
    return "Done"

@app.route('/discoverable', methods=['POST'])
def discoverable():
    """Update "discoverable" boolean"""
    email = request.form['email']
    insert = request.form['status']

    cur = mysql.connection.cursor()

    if insert == 'on':
        cur.execute('''UPDATE Users SET Discoverable = True WHERE Email = (%s)''', (email,))
    elif insert == 'off':
        cur.execute('''UPDATE Users SET Discoverable = False WHERE Email = (%s)''', (email,))

    mysql.connection.commit()
    return "Done"

@app.route('/api/user')
def user_route():
    """Fetches all users"""
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Users''')
    rv = cursor.fetchall()
    return str(rv)

def course_scrape():
    cur = mysql.connection.cursor()
    course_arr = webscraper.scrape_course()
    for course in course_arr:
        cur.execute('''INSERT INTO Courses (CourseCode, CourseName) VALUES (%s,%s)''', (course[0], course[1]))
    mysql.connection.commit()
    return "Scrape Succesful DB Updated"

if __name__ == '__main__':
    app.run(debug=True)
