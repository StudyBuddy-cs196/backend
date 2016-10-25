from flask import Flask, request
from flask_mysqldb import MySQL
from geopy.distance import vincenty
import json
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

@app.route('/register', methods=['POST'])
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
        # get email from request args
        email = request.args.get('email')

        # connect to mysql and execute a search based on given user email
        cur = mysql.connection.cursor()
        cur.execute('''SELECT CourseCode FROM UsersAndCourses WHERE Email = (%s)''', (email,))
        courses = cur.fetchall()

        # iterate through the returned courses and make a final array
        course_tup = ()
        for course in courses:
            cur.execute('''SELECT CourseName FROM Courses WHERE CourseCode = (%s)''', (course[0],))
            course_name = cur.fetchone()
            course_tup += (course[0] +  " " + course_name[0],)

        # build a return a json representation of all 'email' courses
        course_json = {"courses": course_tup}
        return json.dumps(course_json)

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
    """Return matches for user based on course parameter"""
    course = request.args.get('course')
    email = request.args.get('email')
    cur = mysql.connection.cursor()

    cur.execute('''SELECT Latitude, Longitude FROM Users WHERE Email = (%s)''', (email,))
    userLoc = cur.fetchone()
    #finds people who are studying same course

    cur.execute('''SELECT Email FROM UsersAndCourses WHERE CourseCode = (%s)''', (course,))
    courseMatches = cur.fetchall()

    finalMatches = []

    for match in courseMatches:#finds people in database who are discoverable
        tempEmail = match[0]
        print tempEmail
        if tempEmail != email: #make sure email is not email of user
            cur.execute('''SELECT Discoverable FROM Users WHERE Email = (%s)''', (tempEmail,))
            discoverable = cur.fetchone()
            if discoverable[0] == 1:
                finalMatches.append(tempEmail)

    locationMatches = {'matches':[]}

    for matchedEmail in finalMatches: #fill dictionary with user email and distance
        print matchedEmail
        cur.execute('''SELECT Latitude, Longitude FROM Users WHERE Email = (%s)''', (matchedEmail,))
        tempLoc = cur.fetchone()
        locationMatches['matches'].append({
            'email': matchedEmail,
            'lat': tempLoc[0],
            'lng': tempLoc[1],
            'dist': getDistance(tempLoc, userLoc)
        })

    return json.dumps(locationMatches) #return array of matches as JSON file

def getDistance(point1, point2):
    """Return the distance between two given points"""
    return vincenty(point1, point2).miles

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

@app.route('/user')
def user_route():
    """Fetches all users"""
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Users''')
    rv = cursor.fetchall()
    return str(rv)

@app.route('/all_courses')
def all_courses():
    """Fetches all courses"""
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Courses''')
    rv = cursor.fetchall()
    # print dict(rv)
    json_course = []
    for course_tup  in rv:
        json_course.append({
            course_tup[0]: course_tup[1]
        })
    return json.dumps(json_course)
    # return str(rv)

def course_scrape():
    """Scrapes all courses using the module 'webscraper.py'"""
    cur = mysql.connection.cursor()
    course_arr = webscraper.scrape_course()
    for course in course_arr:
        cur.execute('''INSERT INTO Courses (CourseCode, CourseName) VALUES (%s,%s)''', (course[0], course[1]))
    mysql.connection.commit()
    return "Scrape Succesful DB Updated"

if __name__ == '__main__':
    app.run(debug=True)
