import urllib2
from bs4 import BeautifulSoup

base_url = "https://courses.illinois.edu"
semester = "/schedule/2016/fall/"
# opens up the raw html from the fall 2016 schedule
html = urllib2.urlopen(base_url + semester).read()
# use beautiful soup to parse html-->table-->each link
soup = BeautifulSoup(html, 'html.parser')
subject_table = soup.find('table')
links = subject_table.findAll('a')
# iterate through every link found
for link in links:
    # for each link, we want to go in and parse all the classes
    new_link = link.get('href')
    link_html = urllib2.urlopen(base_url + new_link).read()
    soup = BeautifulSoup(link_html, 'html.parser')
    course_table = soup.find('table')
    course_names = course_table.findAll('td')

    # build full course name e.g. "CS 125 Introduction to Computer Science"
    full_name = False
    full_course_name = ""
    for course in course_names:
        full_course_name += " " + course.get_text().strip()
        if full_name:
            print full_course_name # print full name to console
            full_course_name = ""
        full_name = not full_name
