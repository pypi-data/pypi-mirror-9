
import re
import os.path
import sys
import subprocess
from termcolor import colored

# http://git.jiveland.com/?p=core/application.git;a=shortlog;h=refs/heads/release_7.0.2.x
# git clone -b release_7.0.2.x git@git.jiveland.com:core/application.git --depth 1

def __get_url_for_version(version):
    filename = '/usr/local/jiver/git-checkout.txt'
    if not os.path.isfile(filename):
        print colored("Couldn't find " + filename, 'red')
        sys.exit(1)

    infile = open(filename, "r")
    version = version.strip() + " "

    for line in infile:
        line = line.strip()
        #print line
        if line.startswith(version):
            values = line.split()
            return values[1]

    print colored("URL for version " + version + " wasn't found.", 'red')
    print colored("Please see https://brewspace.jiveland.com/docs/DOC-61409 for more information.", 'red')
    sys.exit(1)

def __parse_url_and_do_clone(url, version, depth_1):
    repo = None
    project = None
    branch = None
    try:
        repo = re.search('http://(.+?)(/|\?)', url).group(1)
        project = re.search('p=(.+?)(;|$)', url).group(1)
        branch = re.search('h=(.+?)(;|$)', url).group(1)
        branch_str = re.search('h=(.+?)(;|$)', url).group(1)
        branch = branch_str.split('/')[-1]

    except AttributeError:
        print colored("Format for the URL is unexpected for " + url, 'red')
        print colored("Please see https://brewspace.jiveland.com/docs/DOC-61409 for more information.", 'red')
        sys.exit(1)

    #print repo
    #print project
    #print branch

    user_code_dir = os.path.expanduser("~/code/")
    if version is None:
        version = branch

    cmd = "git clone -b " + branch + " --single-branch git@" + repo + ":" + project + " " + user_code_dir + version

    if depth_1:
        cmd = "git clone -b " + branch + " --single-branch git@" + repo + ":" + project + " --depth 1 " + user_code_dir + version

    print colored(cmd, 'yellow')
    try:
        subprocess.call(cmd.split())
    except KeyboardInterrupt:
        print colored("git command killed", 'red')
        sys.exit(1)




def run(version, depth_1):
    #print "version: " + version
    url = __get_url_for_version(version)
    print colored("Found URL: " + url, 'yellow')

    __parse_url_and_do_clone(url, version, depth_1)

def url(url, depth_1):
    __parse_url_and_do_clone(url, None, depth_1)








