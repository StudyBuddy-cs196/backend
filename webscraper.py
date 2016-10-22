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
    courses = []
    # iterate through every link found
    for link in links:
        # for each link, we want to go in and parse all the classes
        new_link = link.get('href')
        link_html = urllib2.urlopen(base_url + new_link).read()
        soup = BeautifulSoup(link_html, 'html.parser')
        course_table = soup.find('table')
        course_names = course_table.findAll('td')

        course_arr = []
        # Example: course_code = "CS 125" course_name = "Intro to Comp. Sci."
        course_code = ""
        course_name = ""
        full_name = False
        for course in course_names:
            course = course.get_text().strip()
            if full_name:
                course_name = course
                course_arr.append(course_name)
                courses.append(course_arr)
            else:
                course_arr = []
                course_code = course
                course_arr.append(course_code)
            full_name = not full_name
        # print "Scraping..."
    return courses
