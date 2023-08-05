
import sys
import maven_utils
import subprocess
from termcolor import colored
import time
import datetime
import os
import re
import signal

BACKUP_DIR = os.path.expanduser("~/code/DB-BACKUPS")
JIVER_PG_USER = 'postgres'
if os.environ.get('JIVER_PG_USER'):
    JIVER_PG_USER = os.environ.get('JIVER_PG_USER')

def connect():
    os.setpgrp()
    try:
        database_name = maven_utils.find_database_name()
        if database_name:
            cmd = "psql -U" + JIVER_PG_USER + " " + database_name
            print colored("Running '" + cmd + "'", 'yellow')
            return_code = subprocess.call(cmd.split())
    except KeyboardInterrupt:
        print 
        print colored("psql processed killed", 'red')
        os.killpg(0, signal.SIGKILL)
        sys.exit(0)


def create_databases():
    database_name = maven_utils.find_database_name()
    if database_name:
        return_code = create_db(database_name)

    if os.path.isdir("web") & return_code == 0:
       return_code = create_db(database_name + "-eae")

    if return_code == 0:
        return_code = create_db(database_name + "-analytics")

def drop_databases():
    database_name = maven_utils.find_database_name()
    if database_name:
        return_code = drop_db(database_name)

    if os.path.isdir("web") & return_code == 0:
        return_code = drop_db(database_name + "-eae")

    if return_code == 0:
        return_code = drop_db(database_name + "-analytics")

def create_backup_dir_if_needed():
    if not os.path.exists(BACKUP_DIR):
        print colored(BACKUP_DIR + " does not exist. Need to create.", 'red')
        os.makedirs(BACKUP_DIR)
        print colored("Created " + BACKUP_DIR, 'green')

def backup_for(timestamp, database_name):
    filename = database_name + "---" + timestamp + ".sql"
    cmd = "pg_dump -U" + JIVER_PG_USER + " " + database_name + " -f " + BACKUP_DIR + "/" + filename
    print colored(cmd, 'yellow')
    subprocess.call(cmd.split())

def backup():
    create_backup_dir_if_needed()

    database_name = maven_utils.find_database_name()
    current_time = time.time()
    timestamp = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d-%H_%M_%S')

    backup_for(timestamp, database_name)
    backup_for(timestamp, database_name + "-eae")
    backup_for(timestamp, database_name + "-analytics")






def db_name_matcher(filename):
    database_name = maven_utils.find_database_name()
    return re.match( r"^" + database_name + "---", filename)

def eae_name_matcher(filename):
    database_name = maven_utils.find_database_name()
    return re.match( r"^" + database_name + "-eae---", filename)

def analytics_name_matcher(filename):
    database_name = maven_utils.find_database_name()
    return re.match( r"^" + database_name + "-analytics---", filename)

def restore_latest_helper(database_name, database_name_matcher_function):
    #print 'restore_latest()'
    backups = os.listdir(BACKUP_DIR)
    matches = filter(database_name_matcher_function, backups)
    #print matches
    if len(matches) == 0:
        print colored("No backups found for '" + database_name + "' in " + BACKUP_DIR, 'red')
        sys.exit(21)
    else:
        latest = sorted(matches)[-1]
        #print latest

        cmd = "dropdb -U" + JIVER_PG_USER + " " + database_name
        print colored(cmd, 'yellow')
        subprocess.call(cmd.split())

        cmd = "createdb -U" + JIVER_PG_USER + " " + database_name
        print colored(cmd, 'yellow')
        subprocess.call(cmd.split())

        cmd = "psql -U" + JIVER_PG_USER + " " + database_name + " -f " + BACKUP_DIR + '/' + latest
        print colored(cmd, 'yellow')
        subprocess.call(cmd.split())


def restore_latest():
    database_name = maven_utils.find_database_name()
    print

    restore_latest_helper(database_name, db_name_matcher)
    print

    restore_latest_helper(database_name + "-eae", eae_name_matcher)
    print

    restore_latest_helper(database_name + "-analytics", analytics_name_matcher)

def create_db(database_name):
    cmd = "createdb -U" + JIVER_PG_USER + " " + database_name
    print colored("Running '" + cmd + "'", 'yellow')
    return_code = subprocess.call(cmd.split())
    return return_code

def drop_db(database_name):
    cmd = "dropdb -U" + JIVER_PG_USER + " " + database_name
    print colored("Running '" + cmd + "'", 'yellow')
    return_code = subprocess.call(cmd.split())
    return return_code




