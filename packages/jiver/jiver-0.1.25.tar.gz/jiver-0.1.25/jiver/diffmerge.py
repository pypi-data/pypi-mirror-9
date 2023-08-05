
import os
import re
import sys
import subprocess
from termcolor import colored


def __find_file_in_dir(directory, filename):
    if re.search(r'^~', directory):
        directory = os.path.expanduser(directory)

    matches = []
    if os.path.isdir(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                path = os.path.join(root, file)
                if path.endswith('/' + filename):
                    matches.append(path)
    else:
        print colored(directory + " is not a directory", 'red')
        sys.exit(1)

    return matches

def run(dirs, filename):
    paths = []
    for d in dirs:
        matches = __find_file_in_dir(d, filename)
        if len(matches) == 1:
            paths.append(matches[0])
        elif len(matches) > 1:
            print colored("More than one file found for " + filename + " in " + d, 'red')
            print colored("Matches Found:", 'red')
            pre = "\n    "
            print colored(pre + pre.join(matches), 'yellow')
            sys.exit(1)
        else:
            print colored("No file found for " + filename + " in " + d, 'red')

    try:
        cmd = "diffmerge.sh " + " ".join(paths)
        print colored(cmd, 'yellow')
        subprocess.call(cmd.split())
    except KeyboardInterrupt:
        print 
        print colored("Exit diffmerge", 'red')
        sys.exit(1)
