import urllib2
from bs4 import BeautifulSoup

def scrape_course():
    base_url = "https://courses.illinois.edu"
    semester = "/schedule/2016/fall/"
    # opens up the raw html from the fall 2016 schedule
    html = urllib2.urlopen(base_url + semester).read()
    # use beautiful soup to parse html-->table-->each link
    soup = BeautifulSoup(html, 'html.parser')
    subject_table = soup.find('table')
    links = subject_table.findAll('a')
    # object to hold all courses e.g. {"CS 125": "Intro to Comp. Sci.",...}
    # courses = []
    # file to store all course names
    course_file = open('courses.txt', 'w')
    # iterate through every link found
    for link in links:
        # for each link, we want to go in and parse all the classes
        new_link = link.get('href')
        link_html = urllib2.urlopen(base_url + new_link).read()
        soup = BeautifulSoup(link_html, 'html.parser')
        course_table = soup.find('table')
        course_names = course_table.findAll('td')

        # course_arr = []
        # Example: course_code = "CS 125" course_name = "Intro to Comp. Sci."
        course_code = ""
        course_name = ""
        full_name = False
        for course in course_names:
            course = course.get_text().strip()
            if full_name:
                course_name = course
                # course_arr.append(course_name)
                # courses.append(course_arr)
                course_file.write(course_code + " " + course_name + "\n")
            else:
                # course_arr = []
                course_code = course
                # course_arr.append(course_code)
            full_name = not full_name
        # print "Scraping..."
        # break
    course_file.close()
    return "Done scraping!"
    # return courses

def load_courses():
    '''
    Basic function to read all the courses from the text file and parse
    them correctly
    '''
    course_file = open('courses.txt', 'r')
    for course_descrip in course_file:
        # course_descrip = course_file.readline()
        # course_code - "CS 125"
        course_code = ''
        # course_name - "Introduction to Computer Science"
        course_name = ''
        # an array with each course part separated
        course_arr = course_descrip.split()

        course_code = " ".join(course_arr[:2])
        course_name = " ".join(course_arr[2:])
        print course_code
        print course_name
    course_file.close()
