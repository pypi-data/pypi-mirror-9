#!/usr/bin/env python

import os
import sys
import stat
from termcolor import colored
import string
import maven_utils



iterm_run_v5_cmd = """osascript &>/dev/null <<END
    tell application "iTerm"
        make new terminal
        tell the current terminal
            activate current session
            launch session "Default Session"
            tell the last session
                set name to "EAE"
                write text "cd '$MVN_DIR/run-services'"
                write text "./eae-start"
            end tell
        end tell
    end tell
    tell application "iTerm"
        make new terminal
        tell the current terminal
            activate current session
            launch session "Default Session"
            tell the last session
                set name to "WEB"
                write text "cd '$MVN_DIR/web'"
                write text "./cargo-start"
            end tell
        end tell
    end tell
END"""


iterm_run_v6_cmd =  """osascript &>/dev/null <<END
        tell application "iTerm"
            make new terminal
            tell the current terminal
                activate current session
                launch session "Default Session"
                tell the last session
                    set name to "EAE"
                    write text "cd '$MVN_DIR/run-services'"
                    write text "./eae-start"
                end tell
            end tell
        end tell

        if not $NO_SEARCH_SERVICE then
            tell application "iTerm"
                make new terminal
                tell the current terminal
                    activate current session
                    launch session "Default Session"
                    tell the last session
                        set name to "SEARCH"
                        write text "cd '$MVN_DIR/run-services'"
                        write text "./search-start"
                    end tell
                end tell
            end tell
        end if

        tell application "iTerm"
            make new terminal
            tell the current terminal
                activate current session
                launch session "Default Session"
                tell the last session
                    set name to "WEB"
                    write text "cd '$MVN_DIR/web'"
                    write text "./cargo-start"
                end tell
            end tell
        end tell
        tell application "iTerm"
            make new terminal
            tell the current terminal
                activate current session
                launch session "Default Session"
                tell the last session
                    set name to "LOG"
                    write text "tail -f -n 1000 $LOG_PATH"
                end tell
            end tell
        end tell
END"""



terminal_run_v5_cmd = """osascript &>/dev/null <<EOF
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '$MVN_DIR/web'" in window 1
            do script with command "./eae-start" in window 1
        end
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '$MVN_DIR/web'" in window 1
            do script with command "./cargo-start" in window 1
        end tell
EOF"""

terminal_run_v6_cmd = """osascript &>/dev/null <<EOF
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '$MVN_DIR/run-services'" in window 1
            do script with command "./eae-start" in window 1
        end
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end

        if not $NO_SEARCH_SERVICE then
            tell application "Terminal"
                activate
                do script with command "cd '$MVN_DIR/run-services'" in window 1
                do script with command "./search-start" in window 1
            end
            tell application "System Events"
                tell process "Terminal" to keystroke "t" using command down
            end
        end if

        tell application "Terminal"
            activate
            do script with command "cd '$MVN_DIR/web'" in window 1
            do script with command "./cargo-start" in window 1
        end tell
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '$MVN_DIR'" in window 1
            do script with command "tail -f -n 1000 $LOG_PATH" in window 1
        end tell
EOF"""


def exit_invalid_directory():
    print colored("Unable to correctly execute script. Please verify directory.", 'red')
    print colored("Must be at the root of a Jive project", 'red')
    sys.exit(1)

def make_scripts_executable_if_needed(scripts):
    for script in scripts:
        if os.path.isfile(script) and not os.access(script, os.X_OK):
            st = os.stat(script)
            os.chmod(script, st.st_mode | stat.S_IEXEC)


def run_jive_version(mvn_dir, no_search_service, target_log):
    term = os.environ['TERM_PROGRAM']
    log_path = '/usr/local/jive/var/logs/sbs.log'
    if target_log:
        log_path = mvn_dir + '/target/jiveHome/logs/sbs.log'


    if os.path.isdir("run-services"):
        scripts = ['./run-services/eae-start', './run-services/search-start', './web/cargo-start']
        make_scripts_executable_if_needed(scripts)
        if term == "Apple_Terminal":
            template = string.Template(terminal_run_v6_cmd)
            os.system(template.substitute(MVN_DIR = mvn_dir, NO_SEARCH_SERVICE = no_search_service, LOG_PATH = log_path))
        else:
            template = string.Template(iterm_run_v6_cmd)
            os.system(template.substitute(MVN_DIR = mvn_dir, NO_SEARCH_SERVICE = no_search_service, LOG_PATH = log_path))
    else:
        scripts = ['./web/eae-start', './web/cargo-start']
        make_scripts_executable_if_needed(scripts)
        if term == "Apple_Terminal":
            template = string.Template(terminal_run_v5_cmd)
            os.system(template.substitute(MVN_DIR = mvn_dir))
        else:
            template = string.Template(iterm_run_v5_cmd)
            os.system(template.substitute(MVN_DIR = mvn_dir))






#-------------------------------------------------------------------------------
# BEGIN EXECUTION
#-------------------------------------------------------------------------------

def run(no_search_service, target_log):
    mvn_dir = maven_utils.find_root_maven_dir_from_current_dir()
    run_jive_version(mvn_dir, no_search_service, target_log)



