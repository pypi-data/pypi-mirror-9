

import maven_utils

import os
import sys
from termcolor import colored
import string
import xml.etree.ElementTree as ET
import subprocess
import time
import re

pom_xml = """<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <name>themes</name>
    <modelVersion>4.0.0</modelVersion>
    <artifactId>themes</artifactId>
    <packaging>pom</packaging>

    <parent>
        <groupId>$GROUP_ID</groupId>
        <artifactId>$ARTIFACT_ID</artifactId>
        <version>$VERSION</version>
        <relativePath>../pom.xml</relativePath>
    </parent>

    <build>
        <plugins>
            <plugin>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>2.4</version>
                <executions>
                    <execution>
                        <id>plugin-assembly</id>
                        <goals><goal>single</goal></goals>
                        <configuration>
                            <skipAssembly>true</skipAssembly>
                        </configuration>
                    </execution>
                    <execution>
                        <id>theme-assembly</id>
                        <goals><goal>single</goal></goals>
                        <configuration>
                            <skipAssembly>false</skipAssembly>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-antrun-plugin</artifactId>
                <executions>
                    <!-- DO NOT execute the explode-jive-plugin ant tasks -->
                    <execution>
                        <id>explode-jive-plugin</id>
                        <goals><goal>run</goal></goals>
                        <configuration>
                            <skip>true</skip>
                        </configuration>
                    </execution>
                </executions>
            </plugin>

        </plugins>
    </build>
</project>

"""

themes_descriptor_xml = """<?xml version="1.0" encoding="UTF-8"?>
<assembly>
    <id>themes</id>
    <formats>
        <format>zip</format>
    </formats>
    <includeBaseDirectory>false</includeBaseDirectory>
    <fileSets>
        <fileSet>
            <directory>src/main/themes</directory>
            <excludes>
                <exclude>theme.xml</exclude>
            </excludes>
            <outputDirectory>/</outputDirectory>
        </fileSet>
    </fileSets>
</assembly>

"""

def __verify_source_directory_and_create_destination_directory(old_theme_dir, new_theme_dir):
    if not os.path.isdir(old_theme_dir):
        print colored('Themes directory not found in web project', 'red')
        sys.exit(1)
    
    if os.path.isdir(new_theme_dir):
        print colored('New theme directory already exists', 'red')
        sys.exit(1)

    print colored("Found theme directory " + old_theme_dir, 'yellow')
    print colored("Creating " + new_theme_dir, 'yellow')
    os.makedirs(new_theme_dir)

def __print_out_node_information(root):
    for child in root:
        print child.tag, child.attrib
        if child.tag == "groupId":
            group_id = child.attrib
        elif child.tag == "artifactId":
            artifact_id = child.attrib
        elif child.tag == "version":
            version = child.attrib

def __obtain_project_specific_data_from_main_pom_and_create_theme_pom(mvn_dir, new_theme_dir):

    print colored('Extracting info from root pom.xml file.', 'yellow')
    pom_file = mvn_dir + '/pom.xml'
    #print pom_file
    
    group_id = None
    artifact_id = None
    version = None

    root = ET.parse(pom_file).getroot()

    #__print_out_node_information(root)
    nodes = root.find('{http://maven.apache.org/POM/4.0.0}groupId')
    group_id = nodes.text
   
    nodes = root.find('{http://maven.apache.org/POM/4.0.0}artifactId')
    artifact_id = nodes.text
    
    nodes = root.find('{http://maven.apache.org/POM/4.0.0}version')
    version = nodes.text

    print "groupId: " + group_id
    print "artifactId: " + artifact_id
    print "version: " + version
    if len(group_id.strip()) == 0 or len(artifact_id.strip()) == 0 or len(version.strip()) == 0:
        print colored("Wasn't able to find all required info", 'red')
        sys.exit(1)

    f = open(new_theme_dir + "/pom.xml", 'w')
    tmpl = string.Template(pom_xml)
   
    f.write(tmpl.substitute(GROUP_ID = group_id, ARTIFACT_ID = artifact_id, VERSION = version))

def __create_assembly_directory_and_file(new_theme_dir):
    assembly_directory = new_theme_dir + '/src/main/assembly/'
    print colored('Creating ' + assembly_directory, 'yellow')
    os.makedirs(assembly_directory)

    themes_descriptor_file = "themes-descriptor.xml"
    print colored('Creating ' + themes_descriptor_file + ' in ' + assembly_directory, 'yellow')
    f = open(assembly_directory + themes_descriptor_file, 'w')
    f.write(themes_descriptor_xml);

def __svn_move_for_themes_from_web_directory(old_theme_dir, new_theme_dir, jira_ticket):

    print colored("You need to run the following commands manually.", 'red')

    src_main_dir = new_theme_dir + '/src/main/'

    cmd = 'svn add ' + new_theme_dir
    print colored(cmd, 'yellow')
    #subprocess.call(cmd.split())
    time.sleep(2)

    cmd = 'svn mv ' + old_theme_dir + '/ ' + src_main_dir
    print colored(cmd, 'yellow')
    #subprocess.call(cmd.split())

    cmd = 'svn commit -m "' + jira_ticket + ' Moving theme(s) to top level"'
    print colored(cmd, 'yellow')
    #subprocess.call(cmd.split())

def __verify_format_for_jira_ticket(jira_ticket):
    if re.match(r'^[a-zA-Z]+-\d+', jira_ticket):
        return
    else:
        print colored("JIRA ticket is not an expected format: " + jira_ticket, 'red')
        sys.exit(1)



def run(jira_ticket):

    __verify_format_for_jira_ticket(jira_ticket)
    
    mvn_dir = maven_utils.find_root_maven_dir_from_current_dir()

    old_theme_dir = mvn_dir + "/web/src/main/themes"
    new_theme_dir = mvn_dir + "/themes"

    __verify_source_directory_and_create_destination_directory(old_theme_dir, new_theme_dir)

    __obtain_project_specific_data_from_main_pom_and_create_theme_pom(mvn_dir, new_theme_dir)

    __create_assembly_directory_and_file(new_theme_dir)

    __svn_move_for_themes_from_web_directory(old_theme_dir, new_theme_dir, jira_ticket)



