from flask import Flask, request
import psycopg2
import urlparse
# set up flask app
app = Flask(__name__)
conn = psycopg2.connect('postgres://kcfonivufazwlh:6tk-_KIzjcBDOBUoGYFQ3Gc2Df@ec2-50-19-236-35.compute-1.amazonaws.com:5432/d8mq48844a6bjv')
# conn = psycopg2.connect(
#     database="d8mq48844a6bjv",
#     user="kcfonivufazwlh",
#     password="6tk-_KIzjcBDOBUoGYFQ3Gc2Df",
#     host="ec2-50-19-236-35.compute-1.amazonaws.com"
# )

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/users')
def get_users():
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM Users")
    users = ""
    for user in cursor:
        users += str(user) + " "
    return users

if __name__ == '__main__':
    app.run(debug=True)
