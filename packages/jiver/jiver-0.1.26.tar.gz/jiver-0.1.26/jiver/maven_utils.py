

import os
import sys
from xml.dom import minidom
from termcolor import colored



def find_root_maven_dir_from_current_dir():
    cwd = os.getcwd()
    dirs = cwd.split('/')


    highest_dir_with_pom = None

    if 'pom.xml' in os.listdir(cwd):
        highest_dir_with_pom = cwd

    #print 'ABOUT TO LOOP'
    for i in range(1, len(dirs) - 1):
        end_index = -1 * i
        current_dir_path = '/'.join(dirs[0:end_index])
        files_in_current_dir = os.listdir(current_dir_path)
        if 'pom.xml' in files_in_current_dir:
            highest_dir_with_pom = current_dir_path

    if highest_dir_with_pom is None:
        print colored("Doesn't look like you're in a Jive project", 'red')
        sys.exit(1)
    
    return highest_dir_with_pom


def find_jdbc_string():
    highest_dir_with_pom = find_root_maven_dir_from_current_dir()

    if highest_dir_with_pom is None:
        print colored("DIDN'T FIND A pom.xml FILE", 'red')
    else:
        #print "highest_dir_with_pom: " + highest_dir_with_pom

        startup_file = highest_dir_with_pom + "/target/jiveHome/jive_startup.xml"
        if not os.path.isfile(startup_file):
            startup_file = highest_dir_with_pom + "/src/test/resources/jiveHome/jive_startup.xml"
            if not os.path.isfile(startup_file):
                print colored("Could not find jive_startup.xml.", 'red')
                print colored("Expected " + startup_file, 'red')
                print colored("You might not be in a Jive project.", 'red')
                sys.exit(1)

        jive_startup_xml = minidom.parse(startup_file)
        jdbc_string_node = jive_startup_xml.getElementsByTagName("serverURL")[0]
        jdbc_string = jdbc_string_node.firstChild.data
        #print "jdbc_string: " + jdbc_string
        return jdbc_string

def find_database_name():
    jdbc_string = find_jdbc_string()
    if jdbc_string:
        return jdbc_string.split('/')[-1]

    




