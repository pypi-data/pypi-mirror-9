
import maven_utils
import re
import os
import sys
from termcolor import colored
import subprocess

#===============================================================================
# Utilities
#===============================================================================
def __get_path_without_file_name(path):
    dirs = path.split('/')
    return '/'.join(dirs[0:-1])

def __get_file_name(path):
    parts = path.split('/')
    return parts[-1]

def __make_destination_directory_and_extract_file(directory, zip_file, file_path):
    file_path = file_path[1:]
    if not os.path.exists(directory):
        print colored("Creating " + directory, 'yellow')
        os.makedirs(directory)

    cmd = "unzip -p " + zip_file + " " + file_path + " > " + directory + '/' + __get_file_name(file_path)
    print colored(cmd, 'yellow')
    subprocess.Popen(cmd, shell=True)


#===============================================================================
# Handlers
#===============================================================================
def __handle_core_classes(web_dir, zip_file, file_path):
    if file_path.endswith(".java"):
        print colored("Found core class", 'green')
        java_dir = web_dir + '/src/main/java'

        directory = java_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        return True
    return False


def __handle_soy_file(web_dir, zip_file, file_path):
    if file_path.endswith(".soy"):
        print colored("Found soy file", 'green')
        soy_dir = web_dir + '/src/main/webapp'

        directory = soy_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        print colored("Be careful. This file might need to be added to the theme instead.", 'red')
        print colored("Please see https://brewspace.jiveland.com/docs/DOC-74315 for more info.", 'red')
        return True
    return False

def __handle_ftl_files_without_changing_theme(web_dir, zip_file, file_path):
    if file_path.endswith(".ftl"):
        print colored("Found FTL file", 'green')
        my_dir = web_dir + '/src/main/webapp'

        directory = my_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        return True
    return False

def __handle_jive_war_js_file(web_dir, zip_file, file_path):
    if re.match(r'.*\/admin\/scripts\/.*.js', file_path):
        print colored("Found jive-war javascript file", 'green')
        my_dir = web_dir + '/src/main/webapp'

        directory = my_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        return True
    return False

def __handle_core_js_file(web_dir, zip_file, file_path):
    if file_path.endswith(".js"):
        print colored("Found javascript file", 'green')
        my_dir = web_dir + '/src/main/overlay'

        directory = my_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        return True
    return False

def __handle_core_widget_properties(web_dir, zip_file, file_path):
    if re.match(r'^\/beans\/[a-zA-Z_-]+.properties', file_path):
        print colored("Found core widget i18n property file", 'green')
        my_dir = web_dir + '/src/main/webapp/WEB-INF/classes'

        directory = my_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        return True
    return False

def __handle_core_images(web_dir, zip_file, file_path):
    if re.match(r'^\/images\/', file_path):
        print colored("Found core image file", 'green')
        my_dir = web_dir + '/src/main/webapp'

        directory = my_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        return True
    return False

def __handle_404_and_500_page(web_dir, zip_file, file_path):
    if file_path.endswith("404.jsp") or file_path.endswith("500.jsp"):
        print colored("Found 404 or 500 page", 'green')
        my_dir = web_dir + '/src/main/webapp'

        directory = my_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        return True
    return False

def __handle_core_spring_file(web_dir, zip_file, file_path):
    if re.match(r'^\/spring-(\w|-)+.xml', file_path):
        print colored("Found core spring file", 'green')
        my_dir = web_dir + '/src/main/overlay'

        directory = my_dir + __get_path_without_file_name(file_path)
        __make_destination_directory_and_extract_file(directory, zip_file, file_path)
        print colored("Be careful. This file might need to be added to /web/src/main/webapp/WEB-INF/classes/ instead.", 'red')
        print colored("Please see https://brewspace.jiveland.com/docs/DOC-74315 for more info.", 'red')
        return True
    return False


#===============================================================================
# Main
#===============================================================================
def overlay_file(filename):
    parts = filename.split('!')
    if len(parts) == 2:
        highest_dir_with_pom = maven_utils.find_root_maven_dir_from_current_dir()
        web_dir = highest_dir_with_pom + '/web'

        if not os.path.isdir(web_dir):
            print colored("Wasn't able to find the 'web' directory for project.", 'red')
            print colored("You're probably NOT in a Jive project.", 'red')
            sys.exit(1)
        else:
            zip_file = parts[0]
            file_path = parts[1]

            handlers = [ __handle_core_classes,
                __handle_soy_file,
                __handle_ftl_files_without_changing_theme,
                __handle_jive_war_js_file,
                __handle_core_js_file,
                __handle_core_widget_properties,
                __handle_core_images,
                __handle_404_and_500_page,
                __handle_core_spring_file
            ]

            for handler in handlers:
                if handler(web_dir, zip_file, file_path):
                    return

        print colored("Unable to overlay file.", 'red')
        print colored("Please refer to https://brewspace.jiveland.com/docs/DOC-74315", 'red')

    else:
        print colored("Unexpected format for <file>", 'red')
        sys.exit(1)
    None




