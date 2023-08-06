
import re
import os
import sys
import maven_utils
import subprocess
from termcolor import colored
from xml.dom import minidom

def __handle_maven_module(module_dir, should_skip_tests):
        os.chdir(module_dir)

        cmd = "mvn clean package"
        if should_skip_tests:
            cmd += " -DskipTests=true"

        print colored("+" * 120, 'yellow')
        print colored("Running '" + cmd + "' in " + module_dir, 'yellow')
        print colored("+" * 120, 'yellow')

        try:
            return_code = subprocess.call(cmd.split());
            if return_code != 0:
                print colored("Maven process failed", 'red')
                sys.exit(1)
        except KeyboardInterrupt:
            print colored("Maven processed killed", 'red')
            sys.exit(1)


def __startup_tomcat_with_cargo_start_script(web_dir):
    print colored("+" * 80, 'yellow')
    print colored("Running 'cargo-start' in " + web_dir, 'yellow')
    print colored("+" * 80, 'yellow')
    cmd = web_dir +"/cargo-start"
    try:
        subprocess.call(cmd, shell=True);
    except KeyboardInterrupt:
        print colored("Server Shutdown", 'red')
        sys.exit(1)

def __handle_not_found_modules_by_looking_in_web_pom(web_dir, modules_not_found, should_skip_tests):
    web_pom = minidom.parse(web_dir + "/pom.xml")
    if len(web_pom.getElementsByTagName("plugin.dirs")) == 0:
        print colored('plugin.dirs was not available in web/pom.xml', 'red')
        print colored('Unable to run build for modules: ' + " ".join(modules_not_found), 'red')
        sys.exit(1)

    plugin_dirs_node = web_pom.getElementsByTagName("plugin.dirs")[0]

    plugin_dirs = ""
    for node in plugin_dirs_node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            plugin_dirs += node.data

    plugin_dirs = plugin_dirs.replace("\r","")
    plugin_dirs = plugin_dirs.replace("\n","")
    plugin_dirs = plugin_dirs.replace(" ","")
    plugin_dirs = plugin_dirs.replace("\t","")

    original_dir = os.getcwd()
    for module in modules_not_found:
        found = False
        for path in plugin_dirs.split(","):
            if path.endswith(module):
                found = True
                path = re.sub(r'\/target\/.*', '', path)
                __handle_maven_module(path, should_skip_tests)
                break

        if not found:
            print colored("Unable to determine where to find module: " + module, 'red')
            sys.exit(1)

    os.chdir(original_dir)

# ==============================================================================
# Public methods
# ==============================================================================

def for_modules(modules, should_skip_tests):
    root_dir = maven_utils.find_root_maven_dir_from_current_dir()
    original_dir = os.getcwd()
    modules_not_found = []
    for module in modules:
        module_dir = root_dir + "/" + module

        if not os.path.isdir(module_dir):
            modules_not_found.append(module)
            continue

        __handle_maven_module(module_dir, should_skip_tests)


    web_dir = root_dir + "/web"
    os.chdir(web_dir)

    __handle_not_found_modules_by_looking_in_web_pom(web_dir, modules_not_found, should_skip_tests)

    __startup_tomcat_with_cargo_start_script(web_dir)

    os.chdir(original_dir)






