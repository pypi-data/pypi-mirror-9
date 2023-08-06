
import maven_utils
import move_theme_to_top_level


from termcolor import colored
import subprocess
import re
import os
import sys
import time
import stat


import xml.etree.ElementTree as ET
import xml
import tempfile

from string import Template


class PomFile:
    def __init__(self, pomFile):
        root = ET.parse(pomFile).getroot()

        self.path       = pomFile
        self.groupId    = root.find('{http://maven.apache.org/POM/4.0.0}groupId').text
        self.artifactId = root.find('{http://maven.apache.org/POM/4.0.0}artifactId').text
        self.version    = root.find('{http://maven.apache.org/POM/4.0.0}version').text
        modules         = root.find('{http://maven.apache.org/POM/4.0.0}modules')

        self.modulesList = []

        for module in modules:
            if module.text == 'web' or module.text == 'themes' or module.text == 'run-services':
                continue
            self.modulesList.append(module.text)



def __download_jive_maven_unified_archetype_and_get_path_to_jar():
    archetype_version = '1.9'
    cmd = 'mvn org.apache.maven.plugins:maven-dependency-plugin:2.10:get -Dartifact=com.jivesoftware.maven:jive-maven-unified-archetype:' + archetype_version

    print colored("Running the following command to obtain the Jive archetype:", 'yellow')
    print colored(cmd, 'yellow')
    proc = subprocess.Popen(cmd.split())
    exit_code = proc.wait()

    if exit_code == 0:
        jar = os.path.expanduser("~/.m2/repository/com/jivesoftware/maven/jive-maven-unified-archetype/" + archetype_version + "/jive-maven-unified-archetype-" + archetype_version + ".jar");
        if os.path.isfile(jar):
            print colored("\nFound the Jive archetype jar in the expected path: ", 'yellow')
            print colored(jar, 'yellow')
            print "\n"
            return jar
        else:
            print colored("Couldn't find the Jive archetype jar in the expected path: ", 'red')
            print colored(jar, 'red')
            sys.exit(1)
    else:
        print colored("Maven process wasn't able to obtain Jive archetype jar.", 'red')
        sys.exit(1)


def __extract_pom_from_archetype_jar_and_overwrite_current_pom(jarFile, pomFile):
    cmd = "unzip -p " + jarFile + " archetype-resources/pom.xml " + " > " + pomFile.path
    print colored(cmd, 'yellow')
    subprocess.Popen(cmd, shell=True)
    time.sleep(2)

def __extract_from_archetype_jar_and_overwrite(jarFile, jarFilePath, fileToOverwrite):
    cmd = "unzip -p " + jarFile + " archetype-resources/" + jarFilePath  + " > " + fileToOverwrite
    print colored(cmd, 'yellow')
    subprocess.Popen(cmd, shell=True)
    time.sleep(2)

def __substitute_tokens_in_new_pom_file(currentPom, parentPomVersion, pomFile):
    filein = open(pomFile.path)
    tmpl = Template(filein.read())
    result = tmpl.substitute(
                initialProjectVersion = currentPom.version,
                groupId = currentPom.groupId,
                artifactId = currentPom.artifactId,
                parentPomVersion = parentPomVersion
            )

    filein.close()
    time.sleep(2)

    filein = open(pomFile.path, 'w')
    filein.write(result)
    filein.close()
    time.sleep(2)


def __add_modules_from_original_pom_into_new_pom(pomFile):
    tempFile = tempfile.NamedTemporaryFile(delete=False)
    foundClosingModuleTag = False
    with open(pomFile.path) as fp:
        for line in fp:
            if re.match(r'.*</modules>.*', line, re.IGNORECASE):
                foundClosingModuleTag = True
                for module in pomFile.modulesList:
                    node = "        <module>" + module + "</module>\n"
                    tempFile.write(node)
            tempFile.write(line)

    if not foundClosingModuleTag:
        print colored("Closing <module> tag wasn't found in " + pomFile.path, 'red')
        sys.exit(1)

    #print colored("TEMPORARY FILE: " + tempFile.name, 'red')
    #print colored("POM FILE PATH: " + pomFile.path, 'red')
    os.rename(tempFile.name, pomFile.path)


def __upgrade_root_pom(pomFile, jarFile, currentPom, parentPomVersion):

    __extract_pom_from_archetype_jar_and_overwrite_current_pom(jarFile, pomFile)

    __substitute_tokens_in_new_pom_file(currentPom, parentPomVersion, pomFile)

    __add_modules_from_original_pom_into_new_pom(pomFile)

# TODO: make other places use this. Maybe pull it into the maven utils module
def __copy_start_files_from_archetype_jar(mvnDir, jarFile):

    script = mvnDir + "/run-services/eae-start"
    __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/eae-start", script)
    st = os.stat(script)
    os.chmod(script, st.st_mode | stat.S_IEXEC)

    script = mvnDir + "/run-services/search-start"
    __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/search-start", script)
    st = os.stat(script)
    os.chmod(script, st.st_mode | stat.S_IEXEC)

def __copy_pom_file_from_archetype_jar(mvnDir, jarFile, currentPom, parentPomVersion):
    runServicesPom = mvnDir + "/run-services/pom.xml"
    __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/pom.xml", runServicesPom)

    tempFile = tempfile.NamedTemporaryFile(delete=False)

    foundGroupId = False
    foundParentPomVersion = False

    with open(runServicesPom) as fp:
        for line in fp:
            if re.match(r'.*\$\{groupId\}.*', line, re.IGNORECASE):
                foundGroupId = True
                line = line.replace('${groupId}', currentPom.groupId)
            if re.match(r'.*\$\{parentPomVersion\}.*', line, re.IGNORECASE):
                foundParentPomVersion = True
                line = line.replace('${parentPomVersion}', parentPomVersion)

            tempFile.write(line)

    if not foundGroupId or not foundParentPomVersion:
        print colored("All tokens were not found.", 'red')
        sys.exit(1)

    os.rename(tempFile.name, runServicesPom)


def __deal_with_serviceconfig_core_json_file(mvnDir, jarFile, parentPomVersion):
    if parentPomVersion.startswith('6'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/serviceconfig/core.6.json", mvnDir + "/run-services/serviceconfig/core.json")
    elif parentPomVersion.startswith('7'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/serviceconfig/core.6.json", mvnDir + "/run-services/serviceconfig/core.json")
    else:
        print colored("Unexpected version: " + parentPomVersion, 'red')


def __deal_with_main_args_file(mvnDir, jarFile, parentPomVersion):
    if parentPomVersion.startswith('6.0.4'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.6.0.4.properties", mvnDir + "/run-services/main-args.properties")
    elif parentPomVersion.startswith('6.0.5'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.6.0.5.properties", mvnDir + "/run-services/main-args.properties")
    elif parentPomVersion.startswith('6.0.6'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.6.0.6.properties", mvnDir + "/run-services/main-args.properties")
    elif parentPomVersion.startswith('6'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.6.properties", mvnDir + "/run-services/main-args.properties")
    elif parentPomVersion.startswith('7.0.1'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.7.0.1.properties", mvnDir + "/run-services/main-args.properties")
    elif parentPomVersion.startswith('7.0.2'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.7.0.2.properties", mvnDir + "/run-services/main-args.properties")
    elif parentPomVersion.startswith('7.0.3'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.7.0.3.properties", mvnDir + "/run-services/main-args.properties")
    elif parentPomVersion.startswith('7'):
        __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/main-args.7.properties", mvnDir + "/run-services/main-args.properties")

    else:
        print colored("Unexpected version: " + parentPomVersion, 'red')

def __deal_with_var_data_directory_service_files(mvnDir, jarFile):
    __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/var/data/directory/serviceDirectory.json", mvnDir + "/run-services/var/data/directory/serviceDirectory.json")
    __extract_from_archetype_jar_and_overwrite(jarFile, "run-services/var/data/directory/serviceTenanyMappings.json", mvnDir + "/run-services/var/data/directory/serviceTenanyMappings.json")

def upgrade_run_services(mvnDir, jarFile, currentPom, parentPomVersion):
    __copy_start_files_from_archetype_jar(mvnDir, jarFile)
    __copy_pom_file_from_archetype_jar(mvnDir, jarFile, currentPom, parentPomVersion)
    __deal_with_serviceconfig_core_json_file(mvnDir, jarFile, parentPomVersion)
    __deal_with_main_args_file(mvnDir, jarFile, parentPomVersion)
    __deal_with_var_data_directory_service_files(mvnDir, jarFile)

def create_run_services(mvnDir, jarFile, currentPom, parentPomVersion):
    os.makedirs(mvnDir + '/run-services/var/data/directory')
    os.makedirs(mvnDir + '/run-services/serviceconfig')

    __copy_start_files_from_archetype_jar(mvnDir, jarFile)


def __handle_run_services(mvnDir, jarFile, currentPom, parentPomVersion):
    if not os.path.exists(mvnDir + '/run-services'):
        create_run_services(mvnDir, jarFile, currentPom, parentPomVersion)

    upgrade_run_services(mvnDir, jarFile, currentPom, parentPomVersion)


def __upgrade_theme():
    move_theme_to_top_level.run("JIRA-00")

def __obtain_parent_pom_version_to_use(newVersion):
    filename = '/usr/local/jiver/project-upgrade.txt'
    if not os.path.isfile(filename):
        print colored("Couldn't find " + filename, 'red')
        sys.exit(1)

    infile = open(filename, "r")
    newVersion = newVersion.strip()

    foundValues = []
    validValues = []
    for line in infile:
        line = line.strip()
        #print line
        values = line.split('-')
        validValues.append(values[0])
        if line.startswith(newVersion):
            foundValues.append(line)


    if len(foundValues) > 1:
        print colored(newVersion + " is an ambiguous value.", 'red')
        print colored("VALID VALUES: ", 'red')
        print colored("\n".join(validValues), 'red')
        sys.exit(1)
    elif len(foundValues) == 1:
        return foundValues[0]


    print colored(newVersion + " wasn't found in " + filename, 'red')
    sys.exit(1)

def __upgrade_web_pom(mvnDir, jarFile, currentPom):
    pom_xml = mvnDir + "/web/pom.xml"
    __extract_from_archetype_jar_and_overwrite(jarFile, "web/pom.xml", pom_xml)

    tempFile = tempfile.NamedTemporaryFile(delete=False)

    foundGroupId = False
    foundRootArtifactId = False
    foundInitialProjectVersion = False

    with open(pom_xml) as fp:
        firstLine = True
        for line in fp:
            if firstLine:
                firstLine = False
                continue

            if re.match(r'.*\$\{groupId\}.*', line, re.IGNORECASE):
                foundGroupId = True
                line = line.replace('${groupId}', currentPom.groupId)

            if re.match(r'.*\$\{rootArtifactId\}.*', line, re.IGNORECASE):
                foundRootArtifactId = True
                line = line.replace('${rootArtifactId}', currentPom.artifactId)

            if re.match(r'.*\$\{initialProjectVersion\}.*', line, re.IGNORECASE):
                foundInitialProjectVersion = True
                line = line.replace('${initialProjectVersion}', currentPom.version)

            tempFile.write(line)

    if not foundGroupId or not foundRootArtifactId or not foundInitialProjectVersion:
        print colored("All tokens were not found.", 'red')
        sys.exit(1)

    os.rename(tempFile.name, pom_xml)

def user_verification():
    print colored("This is an experimental feature.\nAny changes made should be verified before committing to the source repository.", 'red')
    while(True):
        typedValue = raw_input("Accept? Please type 'YES' or 'NO': ")
        if typedValue == 'NO':
            print colored("Goodbye", 'red')
            sys.exit(0)
        elif typedValue == 'YES':
            print colored("Starting the upgrade process.", 'green')
            break


def upgrade(newVersion):

    user_verification()
    parentPomVersion = __obtain_parent_pom_version_to_use(newVersion)

    mvnDir     = maven_utils.find_root_maven_dir_from_current_dir()
    pomFile    = mvnDir + '/pom.xml'
    jarFile    = __download_jive_maven_unified_archetype_and_get_path_to_jar()
    currentPom = PomFile(pomFile)

    #print currentPom.version
    #print currentPom.artifactId
    #print currentPom.groupId
    #print currentPom.modulesList

    __upgrade_root_pom(currentPom, jarFile, currentPom, parentPomVersion)
    __handle_run_services(mvnDir, jarFile, currentPom, parentPomVersion)
    __upgrade_web_pom(mvnDir, jarFile, currentPom)
    __upgrade_theme()



