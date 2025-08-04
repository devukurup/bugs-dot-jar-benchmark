import os
from os.path import join
from pprint import pprint
import shutil
import urllib.request
import json
from pprint import pprint


metadata = open("meta-data.json","r")

projects = json.load(metadata)

metadata.close()

for project in projects:
    
    # Skip if branch doesn't contain "hotfix"
    if 'hotfix' not in project['branch'].lower():
        continue
    
    os.makedirs(project["subject"],exist_ok=True)
    os.makedirs(join(project["subject"],project["bug_id"]),exist_ok=True)

    shutil.copy2("build_subject",join(project["subject"],project["bug_id"],"build_subject"))
    shutil.copy2("clean_subject",join(project["subject"],project["bug_id"],"clean_subject"))
    shutil.copy2("compress_deps",join(project["subject"],project["bug_id"],"compress_deps"))
    shutil.copy2("config_subject",join(project["subject"],project["bug_id"],"config_subject"))
    shutil.copy2("install_deps",join(project["subject"],project["bug_id"],"install_deps"))
    shutil.copy2("run_test",join(project["subject"],project["bug_id"],"run_test"))
    shutil.copy2("setup_subject",join(project["subject"],project["bug_id"],"setup_subject"))
    shutil.copy2("verify_dev",join(project["subject"],project["bug_id"],"verify_dev"))
    
    # Get Java version from metadata
    java_version = project.get('java_version', 8)  # Default to Java 8 if not specified
    
    # Update install_deps with correct Java version
    os.system("sed -i 's/openjdk-[0-9]*-jdk/openjdk-{}-jdk/' {}".format(java_version, join(project["subject"],project["bug_id"],"install_deps")))
    
    x = project["project_name"].rstrip('/')  # Remove trailing slash safely
    os.system("sed -i 's/<BRANCH>/{}/' {}".format(project['branch'],join(project["subject"],project["bug_id"],"setup_subject")))
    os.system("sed -i 's/<SUBJECT>/{}/' {}".format(project['subject'],join(project["subject"],project["bug_id"],"setup_subject")))

    if x:  # Only process if project_name is not empty
        # Escape forward slashes for sed compatibility
        escaped_x = x.replace('/', r'\/')
        
        os.system("sed -i '0,/<SUB_PROJECT>/s/<SUB_PROJECT>/{}/' {}".format(escaped_x, join(project["subject"],project["bug_id"],"run_test")))
        os.system("sed -i '0,/<SUB_PROJECT>/s/<SUB_PROJECT>/{}/' {}".format(escaped_x, join(project["subject"],project["bug_id"],"build_subject")))
        os.system("sed -i '0,/<SUB_PROJECT>/s/<SUB_PROJECT>/{}/' {}".format(escaped_x, join(project["subject"],project["bug_id"],"clean_subject")))
        os.system("sed -i '0,/<SUB_PROJECT>/s/<SUB_PROJECT>/{}/' {}".format(escaped_x, join(project["subject"],project["bug_id"],"compress_deps")))

    else:
        # Empty project_name means build entire project (keep <SUB_PROJECT> placeholder)
        print(f"Empty project_name for {project['id']} - will build entire project")
