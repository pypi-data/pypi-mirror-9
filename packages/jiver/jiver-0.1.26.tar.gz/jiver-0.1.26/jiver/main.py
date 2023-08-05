#!/usr/bin/env python
"""
Usage:
     jiver build-and-run [--skip-tests] <maven-module>...
     jiver core-checkout [--depth-1] <version>
     jiver core-checkout-url [--depth-1] <url>
     jiver create (project | plugin)
     jiver database (connect | backup | restore-latest | create-project-databases | drop-project-databases)
     jiver diffmerge <directory-1> <directory-2> <file>
     jiver diffmerge <directory-1> <directory-2> <directory-3> <file>
     jiver move-theme-to-top-level <JIRA-ticket>
     jiver overlay <file>
     jiver run-tabs
     jiver upgrade-analyzer
     jiver vpn (all | split | my-current-gateway)


Options:
    -h --help     Show this screen.
    -v --version  Show version.

Documentation:
     \033[1mjiver build-and-run\033[0m
            Command gives you the ability to run maven builds for multiple plugins/modules for a Jive project in sequence and then run the
            cargo-start script. This command can run in any subdirectory of a Jive project.

            Example:
                jiver build-and-run --skip-tests retention user-sync web

                This will run 'mvn clean package -DskipTest=true' for retention, then user-syc, and finally web. Once successfully built,
                the cargo-start script will run.

     \033[1mjiver core-checkout\033[0m
            Command will checkout a version of core code. This command works with tab completion for the Jive version numbers. The version
            numbers can be found in /usr/local/jiver/git-checkout.txt. This config file was generated from
            https://brewspace.jiveland.com/docs/DOC-61409.

            Example:
                jiver core-checkout --depth-1 7.0.0.2

                This will clone the code for 7.0.0.2 in ~/code. It will only obtain one log message. This helps to minimize the size of the
                checkout.

     \033[1mjiver core-checkout-url\033[0m
            Similar to 'jiver core-checkout', but for a URL. You can use the urls from https://brewspace.jiveland.com/docs/DOC-61409.

            Example:
                jiver core-checkout-url --depth-1 'http://git.jiveland.com/?p=core/application.git;a=shortlog;h=refs/heads/release_7.0.2.x'

     \033[1mjiver create\033[0m
            Used to create a project or a plugin

            \033[1mproject\033[0m
                Runs 'mvn -U jive:create-project'
            \033[1mplugin\033[0m
                Runs 'mvn -U jive:create-plugin'

     \033[1mjiver database\033[0m
            All of these commands must run while in a Jive project directory or subdirectory. The command defaults to using the 'postgres'
            user. You can change this by using the environment variable JIVER_PG_USER. For example, 'export JIVER_PG_USER=testuser'.

            \033[1mcreate-project-databases\033[0m
                Will create Application, EAE and Analytics database via createdb using configured jdbc value in JIVE_PROJECT/target/jiveHome/jive_startup.xml.
                The EAE database will only be created for Jive versions 5 and above
            \033[1mcreate-iproject-databases\033[0m
                Will drop Application, EAE and Analytics database via dropdb using configured jdbc value in JIVE_PROJECT/target/jiveHome/jive_startup.xml.
                The EAE database will only be dropped in Jive versions 5 and above
            \033[1mconnect\033[0m
                Will automatically connect via psql to the configured jdbc value in JIVE_PROJECT/target/jiveHome/jive_startup.xml
            \033[1mbackup\033[0m
                Will back up the databases (main, eae, analytics) for the current Jive project with a timestamp to ~/code/DB-BACKUPS. This
                requires the user to conform to database names like the following:
                    mcgrawhill
                    mcgrawhill-eae
                    mcgrawhill-analytics
            \033[1mrestore-latest\033[0m
                Restores the most recent backup in ~/code/DB-BACKUPS for the current Jive project.

     \033[1mjiver diffmerge\033[0m
            Given two or three directories, this will look for the given filename. This searches all the directories for the filename and
            opens them in diffmerge.sh.

            Exmaple:
                jiver diffmerge ~/code/7.0.0.1 ~/code/7_0_3_1_core_ga login.ftl

                This generates the following command:
                diffmerge.sh \\
                ~/code/7.0.0.1/application/war/src/main/webapp/WEB-INF/classes/template/global/login.ftl \\
                ~/code/7_0_3_1_core_ga/war/src/main/webapp/WEB-INF/classes/template/global/login.ftl

            If multiple files are found, you can pass in a more specific string for the filename

            Example:
                jiver diffmerge ~/code/7.0.0.1 ~/code/7_0_3_1_core_ga global/login.ftl

                Notice the filename has 'global/' added to it.


     \033[1mjiver move-theme-to-top-level\033[0m
            Will move the theme(s) from the 'web' directory to at top level maven module. <JIRA-ticket> will be used for subversion commits during this process. It's recommended to use a Jira ticket specifically for this task.

     \033[1mjiver overlay\033[0m
            Give ths user the ability to overlay a file per the rules defined on https://brewspace.jiveland.com/docs/DOC-74315. You must be
            in a Jive project to run this command.

            Example:
                jiver overlay '/Users/mike.masters/.m2/repository/com/jivesoftware/jive-core/7.0.3.1_5dfcca9/jive-core-7.0.3.1_5dfcca9-sources.jar!/com/jivesoftware/community/aaa/sso/saml/filter/JiveLocalMessageStorageSAMLEntryPoint.java'

                This will overlay JiveLocalMessageStorageSAMLEntryPoint.java by extracting the file from the source jar and placing the file
                accordingly in the 'web' directory of the Jive project. You can obtain the file argument by using the following steps:

                1. Open the Jive project for the customer in Intellij.
                2. Press <command>-<shift>-<n> to search for the file you want to overlay. Make sure 'Include non-project files' has a
                    checkmark next to it.
                3. Right click on the tab the source file is open in.
                4. Click 'Copy Path'.
                5. Paste value in the console with the command. Make sure to have the path value enclosed in single quotes. There should be
                    an exclamation in the string. This will be interpreted by bash/zsh.


     \033[1mjiver run-tabs\033[0m
            Please see https://brewspace.jiveland.com/people/mike.masters/blog/2013/11/21/automated-tabs-and-services

     \033[1mjiver upgrade-analyzer\033[0m
            Please see https://brewspace.jiveland.com/community/ps/ps_engineering/blog/2014/10/17/upgrade-analyzer for additional info. This
            command will start up the upgrade analyzer installed with the 'jiver' command. The upgrade analyzer is available in
            /usr/local/jiver.

     \033[1mjiver vpn\033[0m
            Please see https://brewspace.jiveland.com/docs/DOC-167753 for more info. This command automates the steps from that doc.

            \033[1mall\033[0m
                Saves the current gateway value and sends all traffic through the VPN.
            \033[1msplit\033[0m
                Uses the previously saved gateway value and splits the VPN traffic.
            \033[1mmy-current-gateway\033[0m
                Displays the current gateway value.

"""

from docopt import docopt
from jiver import __version__

from termcolor import colored
import subprocess
import sys
import os
import signal

import tabs
import build_and_run
import database
import vpn
import diffmerge
import overlay
import move_theme_to_top_level
import core_checkout



def start():
    version = ".".join(str(x) for x in __version__)
    arguments = docopt(__doc__, version=version)

    if arguments.get('core-checkout', None):
        version = arguments['<version>']
        depth_1 = arguments['--depth-1']
        core_checkout.run(version, depth_1)

    elif arguments.get('core-checkout-url', None):
        url = arguments['<url>']
        depth_1 = arguments['--depth-1']
        core_checkout.url(url, depth_1)

    elif arguments.get('build-and-run', None):
        maven_modules = arguments['<maven-module>']
        skip_tests = arguments['--skip-tests']
        build_and_run.for_modules(maven_modules, skip_tests)

    elif arguments.get('create', None):
        if arguments['project']:
            try:
                cmd = "mvn -U jive:create-project"
                print colored("Running '" + cmd + "'", 'yellow')
                return_code = subprocess.call(cmd.split())
            except KeyboardInterrupt:
                print colored("Maven processed killed", 'red')
                sys.exit(0)
        elif arguments['plugin']:
            try:
                cmd = "mvn -U jive:create-plugin"
                print colored("Running '" + cmd + "'", 'yellow')
                return_code = subprocess.call(cmd.split())
            except KeyboardInterrupt:
                print colored("Maven processed killed", 'red')
                sys.exit(0)

    elif arguments.get('upgrade-analyzer', None):
        os.setpgrp()
        try:
            cmd = "java -jar /usr/local/jiver/upgrade-analyzer.jar port=9000"
            print colored("Running '" + cmd + "'", 'yellow')
            return_code = subprocess.call(cmd.split())
        except KeyboardInterrupt:
            print colored("Processed killed", 'red')
            os.killpg(0, signal.SIGKILL)
            sys.exit(0)

    elif arguments.get('database', None):
        if arguments['connect']:
            database.connect()
        elif arguments['backup']:
            database.backup()
        elif arguments['restore-latest']:
            database.restore_latest()
        elif arguments['create-project-databases']:
            database.create_databases()
        elif arguments['drop-project-databases']:
            database.drop_databases()

    elif arguments.get('move-theme-to-top-level', None):
        jira_ticket = arguments['<JIRA-ticket>']
        move_theme_to_top_level.run(jira_ticket)

    elif arguments.get('diffmerge', None):
        d1 = arguments['<directory-1>']
        d2 = arguments['<directory-2>']
        d3 = arguments['<directory-3>']
        filename = arguments['<file>']
        diffmerge.run(filter(None, [d1, d2, d3]), filename)

    elif arguments.get('vpn', None):
        if arguments['all']:
            vpn.all()
        elif arguments['split']:
            vpn.split()
        elif arguments['my-current-gateway']:
            vpn.my_current_gateway()

    elif arguments.get('overlay', None):
        filename = arguments['<file>']
        overlay.overlay_file(filename)

    elif arguments.get('run-tabs', None):
        tabs.run()



