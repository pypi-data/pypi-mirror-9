
import re
import sys
import os
import subprocess
from subprocess import PIPE

from termcolor import colored

# TODO: need to create a util to make sure this exists
JIVER_HOME = os.path.expanduser("~/.jiver")
vpn_ip_file = JIVER_HOME + '/vpn_ip'

def __obtain_default_gateway_and_save_to_file():
    cmd = "route -n get default | grep gateway | sed 's/.*gateway: //'"
    p = subprocess.Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()
    default_gateway = output[0].rstrip()

    print colored("Current default gateway: " + default_gateway, 'yellow')
    print colored("Saving to " + vpn_ip_file, 'yellow')
    if not os.path.isdir(JIVER_HOME):
        os.makedirs(JIVER_HOME)

    f = open(vpn_ip_file, 'w')
    f.write(default_gateway)

def __force_all_traffic_through_the_vpn_connection():

    try:
        cmd = "netstat -r | grep  '10\.61' | awk '{print $6}' | sort | uniq"
        p = subprocess.Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()
        if len(output) != 2:
            print colored("Found multiple interfaces.", 'red')
            print output
            sys.exit(1)

        interface = output[0].strip()
        print colored("Interface: " + interface, 'yellow')

        cmd = "sudo route change default -link -interface " + interface
        print colored(cmd, 'yellow')
        subprocess.call(cmd.split())
    except KeyboardInterrupt:
        sys.exit(1)

def __get_saved_default_gateway_or_most_likely_value():
    saved_default_gateway = ""
    try:
        f = open(vpn_ip_file, 'r')
        saved_default_gateway = f.read()
    except IOError:
        None # Do nothing

    if not re.search(r'^\d+\.\d+\.\d+\.\d+$', saved_default_gateway):
        print colored("Malformed or missing data in " + vpn_ip_file, 'red')
        print colored("Using 192.168.1.1 for the default gateway.", 'red')
        print colored("Press control-c if you don't want to proceed.", 'red')
        print colored("You can try rebooting your computer instead.", 'red')
        return "192.168.1.1"

    return saved_default_gateway


def __change_default_gateway(gateway):
    cmd = "sudo route change default " + gateway
    print colored(cmd, 'yellow')
    try:
        subprocess.call(cmd.split())
    except KeyboardInterrupt:
        sys.exit(1)




# ==============================================================================
# Public methods
# ==============================================================================
def all():
    __obtain_default_gateway_and_save_to_file()
    __force_all_traffic_through_the_vpn_connection()


def split():
    gateway = __get_saved_default_gateway_or_most_likely_value()
    __change_default_gateway(gateway)


def my_current_gateway():
    cmd = "route -n get default | grep gateway"
    print colored(cmd, 'yellow')
    p = subprocess.Popen(cmd, shell=True, stdout=PIPE)
    print p.communicate()[0]
