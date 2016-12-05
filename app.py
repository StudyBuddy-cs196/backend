from flask import Flask, request
import psycopg2
from geopy.distance import vincenty
import json
from datetime import datetime
import webscraper
import os

# set up flask app
app = Flask(__name__)

# configure postgres database connection
connection = psycopg2.connect(os.environ['DATABASE_URL'])


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/is_registered', methods=['GET'])
def is_registered():
    email = request.args.get('email')
    if check_registered(email):
        return "true"
    else:
        return "false"

def check_registered(email):
    cursor = connection.cursor()
    cursor.execute('''SELECT email FROM Users WHERE email = (%s)''', (email,))
    user = cursor.fetchone()
    if user:
        return True
    else:
        return False

@app.route('/register', methods=['POST'])
def register_route():
    """Register user into database or update their credentials"""
    # get name and email from request form
    email = request.form['email']
    name = request.form['name']
    bio = request.form['bio']
    picture = request.form['picture']
    cursor = connection.cursor()

    # check if the user is already registered
    if check_registered(email):
        cursor.execute('''UPDATE Users SET email=(%s),name=(%s),bio=(%s),picture=(%s) WHERE email=(%s)''', (email,name,bio,picture,email))
        connection.commit()
        return "Already registered"

    # execute an insert into the DB
    cursor.execute('''INSERT INTO Users (email, name, bio, picture, courses, latitude, longitude, discoverability) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (email,name,bio,picture,'{}',"40.1141","-88.2243", "true"))
    connection.commit()
    return "Done"

@app.route('/get_user', methods=['GET'])
def get_user():
    email = request.args.get('email')
    cursor = connection.cursor()
    cursor.execute('''SELECT email, name, bio, picture, courses, latitude, longitude, discoverability FROM Users WHERE email=(%s)''', (email,))
    userObj = cursor.fetchone()

    user = {
        'email': userObj[0],
        'name': userObj[1],
        'bio': userObj[2],
        'picture': userObj[3],
        'courses': userObj[4],
        'latitude': float(userObj[5]),
        'longitude': float(userObj[6]),
        'discoverability': userObj[7]
    }
    print user
    return json.dumps(user)


@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if (request.method == 'GET'):
        # get email from request args
        email = request.args.get('email')

        # connect to mysql and execute a course search based on given user email
        cur = connection.cursor()
        cur.execute('''SELECT courses from Users WHERE email = (%s)''', (email,))
        courses = cur.fetchone()[0]
        print email + " has these courses: " + str(courses)

        # iterate through returned courses to make full course names
        course_tup = ()
        for course in courses:
            cur.execute('''SELECT coursename FROM Courses WHERE coursecode = (%s)''', (course,))
            course_name = cur.fetchone()
            course_tup += (course +  " " + course_name[0],)

        # build a returnable json representation of all of email's courses
        course_json = {"courses": course_tup}
        return json.dumps(course_json)

    elif (request.method == 'POST'):
        email = request.form['email']
        add = request.form['status']
        course = request.form['course']
        cur = connection.cursor()
        cur.execute('''SELECT courses FROM Users WHERE email = (%s)''', (email,))
        # get the user's courses as an array
        user_courses = cur.fetchone()[0]
        # checks if we want to add and the user doesn't already have the course
        if add == "True" and course not in user_courses:
            print "ready to add the course"
            user_courses.append(course)
            cur.execute('''UPDATE Users SET courses=%s WHERE email=(%s)''', (user_courses, email))
        # checks if we want to drop and the user has the course already
        if add == "False" and course in user_courses:
            print "dropping the course"
            user_courses.remove(course)
            cur.execute('''UPDATE Users SET courses=%s WHERE email=(%s)''', (user_courses, email))

        connection.commit()
    return "Done"

@app.route('/matches', methods=['GET'])
def matches():
    """Return matches for user based on course parameter"""
    course = request.args.get('course')
    email = request.args.get('email')
    cur = connection.cursor()

    # get your own location
    cur.execute('''SELECT latitude, longitude FROM Users WHERE email=(%s)''', (email,))
    my_location = cur.fetchone()

    # find users that are discoverable
    cur.execute('''SELECT courses, email, name, latitude, longitude, bio, picture FROM Users WHERE discoverability=TRUE and email<>(%s)''', (email,))
    initial_matches = cur.fetchall()
    print initial_matches

    course_matches = []
    # narrow users down by course
    for match in initial_matches:
        courses = match[0]
        if course in courses:
            course_matches.append(match)

    print "these are the matches that match by course"
    print course_matches

    # convert my location from previous query to float values and tupleize it
    my_loc = (float(my_location[0]), float(my_location[1]))

    final_matches = {'matches':[]}
    for match in course_matches:
        location = (float(match[3]), float(match[4]))
        final_matches['matches'].append({
            'email': match[1],
            'name': match[2],
            'lat': location[0],
            'lng': location[1],
            'bio': match[5],
            'picture': match[6],
            'dist': getDistance(my_loc, location)
        })
    return json.dumps(final_matches)

def getDistance(point1, point2):
    """Return the distance between two given points"""
    return vincenty(point1, point2).miles

@app.route('/location', methods=['POST'])
def location():
    """Update location (latitude/longitude) of given user"""
    email = request.form['email']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    cur = connection.cursor()

    cur.execute('''UPDATE Users SET latitude = %s WHERE email = (%s)''', (latitude,email,))
    cur.execute('''UPDATE Users SET longitude = %s WHERE email = (%s)''', (longitude,email,))
    cur.execute('''UPDATE Users SET checkin = %s WHERE email = (%s)''', (datetime.now(), email,))
    print("This is the time" + str(datetime.now()))
    connection.commit()
    return "Done"

@app.route('/discoverable', methods=['POST'])
def discoverable():
    """Update "discoverable" boolean"""
    email = request.form['email']
    insert = request.form['status']

    cur = connection.cursor()

    if insert == 'on':
        cur.execute('''UPDATE Users SET discoverability = True WHERE email = (%s)''', (email,))
    elif insert == 'off':
        cur.execute('''UPDATE Users SET discoverability = False WHERE email = (%s)''', (email,))

    connection.commit()
    return "Done"

@app.route('/user')
def user_route():
    """Fetches all users"""
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM Users''')
    rv = cursor.fetchall()
    return str(rv)

@app.route('/all_courses')
def all_courses():
    """Fetches all courses"""
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM Courses''')
    rv = cursor.fetchall()
    json_course = []
    for course_tup  in rv:
        json_course.append({
            course_tup[0]: course_tup[1]
        })
    return json.dumps(json_course)


def course_load():
    """
    Loads all courses using the text file generated from
    the module 'webscraper.py'
    """
    cur = connection.cursor()
    # open the file with all the courses scraped
    course_file = open('courses.txt', 'r')
    for course_descrip in course_file:
        # course_descrip = course_file.readline()
        # course_code - "CS 125"
        course_code = ''
        # course_name - "Introduction to Computer Science"
        course_name = ''
        # an array with each course part separated
        course_arr = course_descrip.split()
        # splice for the individual parts we care about
        course_code = " ".join(course_arr[:2])
        course_name = " ".join(course_arr[2:])
        cur.execute('''INSERT INTO Courses (coursecode, coursename) VALUES (%s,%s)''', (course_code, course_name))
    course_file.close()

    connection.commit()
    return "Scrape Succesful DB Updated"

if __name__ == '__main__':
    app.run(debug=True)
