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
    
    x = project["project_name"][:-1]
    os.system("sed -i 's/<BRANCH>/{}/' {}".format(project['branch'],join(project["subject"],project["bug_id"],"setup_subject")))
    os.system("sed -i 's/<SUBJECT>/{}/' {}".format(project['subject'],join(project["subject"],project["bug_id"],"setup_subject")))
    
    if '/' in x:
        print(x)
        print(project["id"],project["subject"])
        #input()
    else:
        os.system("sed -i '0,/<SUB_PROJECT>/s/<SUB_PROJECT>/{}/' {}".format(x,join(project["subject"],project["bug_id"],"run_test")))
        os.system("sed -i '0,/<SUB_PROJECT>/s/<SUB_PROJECT>/{}/' {}".format(x,join(project["subject"],project["bug_id"],"build_subject")))
