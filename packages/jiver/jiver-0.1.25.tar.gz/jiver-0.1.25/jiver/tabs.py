#!/usr/bin/env python

import os
import sys
import stat
from termcolor import colored

CWD = os.getcwd()

iterm_run_v5_cmd = """osascript &>/dev/null <<END
    tell application "iTerm"
        make new terminal
        tell the current terminal
            activate current session
            launch session "Default Session"
            tell the last session
                set name to "EAE"
                write text "cd '%(CWD)s/run-services'"
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
                write text "cd '%(CWD)s/web'"
                write text "./cargo-start"
            end tell
        end tell
    end tell
END""" % locals()


iterm_run_v6_cmd =  """osascript &>/dev/null <<END
        tell application "iTerm"
            make new terminal
            tell the current terminal
                activate current session
                launch session "Default Session"
                tell the last session
                    set name to "EAE"
                    write text "cd '%(CWD)s/run-services'"
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
                    set name to "SEARCH"
                    write text "cd '%(CWD)s/run-services'"
                    write text "./search-start"
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
                    write text "cd '%(CWD)s/web'"
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
                    write text "tail -f -n 1000 /usr/local/jive/var/logs/sbs.log"
                end tell
            end tell
        end tell
END""" % locals()



terminal_run_v5_cmd = """osascript &>/dev/null <<EOF
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '%(CWD)s/web'" in window 1
            do script with command "./eae-start" in window 1
        end
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '%(CWD)s/web'" in window 1
            do script with command "./cargo-start" in window 1
        end tell
EOF""" % locals()

terminal_run_v6_cmd = """osascript &>/dev/null <<EOF
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '%(CWD)s/run-services'" in window 1
            do script with command "./eae-start" in window 1
        end
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '%(CWD)s/run-services'" in window 1
            do script with command "./search-start" in window 1
        end
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '%(CWD)s/web'" in window 1
            do script with command "./cargo-start" in window 1
        end tell
        tell application "System Events"
            tell process "Terminal" to keystroke "t" using command down
        end
        tell application "Terminal"
            activate
            do script with command "cd '%(CWD)s'" in window 1
            do script with command "tail -f -n 1000 /usr/local/jive/var/logs/sbs.log" in window 1
        end tell
EOF""" % locals()


def exit_invalid_directory():
    print colored("Unable to correctly execute script. Please verify directory.", 'red')
    print colored("Must be at the root of a Jive project", 'red')
    sys.exit(1)

def make_scripts_executable_if_needed(scripts):
    for script in scripts:
        if os.path.isfile(script) and not os.access(script, os.X_OK):
            st = os.stat(script)
            os.chmod(script, st.st_mode | stat.S_IEXEC)


def verify_correct_directory_and_run_jive_version():
    term = os.environ['TERM_PROGRAM']


    if os.path.isdir("web"):
        if os.path.isdir("run-services"):
            scripts = ['./run-services/eae-start', './run-services/search-start', './web/cargo-start']
            make_scripts_executable_if_needed(scripts)
            if term == "Apple_Terminal":
                os.system(terminal_run_v6_cmd)
            else:
                os.system(iterm_run_v6_cmd)
        else:
            scripts = ['./web/eae-start', './web/cargo-start']
            make_scripts_executable_if_needed(scripts)
            if term == "Apple_Terminal":
                os.system(terminal_run_v5_cmd)
            else:
                os.system(iterm_run_v5_cmd)

    else:
        exit_invalid_directory()



#-------------------------------------------------------------------------------
# BEGIN EXECUTION
#-------------------------------------------------------------------------------

def run():
    verify_correct_directory_and_run_jive_version()



