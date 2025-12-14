import os
from os.path import join
import shutil
import json


metadata = open("meta-data.json","r")

projects = json.load(metadata)

metadata.close()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

for project in projects:

    # Skip if branch doesn't contain "hotfix"
    if 'hotfix' not in project['branch'].lower():
        continue

    os.makedirs(project["subject"],exist_ok=True)
    os.makedirs(join(project["subject"],project["bug_id"]),exist_ok=True)

    # Determine template directory based on build system
    build_system = project.get('build_system', 'maven')
    if build_system == 'gradle':
        template_dir = join(script_dir, "gradle", "base")
    elif build_system == 'ant':
        template_dir = join(script_dir, "ant", "base")
    else:
        # Default to Maven (root directory templates)
        template_dir = script_dir

    shutil.copy2(join(template_dir, "build_subject"),join(project["subject"],project["bug_id"],"build_subject"))
    shutil.copy2(join(template_dir, "clean_subject"),join(project["subject"],project["bug_id"],"clean_subject"))
    shutil.copy2(join(template_dir, "compress_deps"),join(project["subject"],project["bug_id"],"compress_deps"))
    shutil.copy2(join(template_dir, "config_subject"),join(project["subject"],project["bug_id"],"config_subject"))
    shutil.copy2(join(template_dir, "install_deps"),join(project["subject"],project["bug_id"],"install_deps"))
    shutil.copy2(join(template_dir, "run_test"),join(project["subject"],project["bug_id"],"run_test"))
    shutil.copy2(join(template_dir, "setup_subject"),join(project["subject"],project["bug_id"],"setup_subject"))
    shutil.copy2(join(template_dir, "verify_dev"),join(project["subject"],project["bug_id"],"verify_dev"))
    shutil.copy2(join(template_dir, "verify_patches"),join(project["subject"],project["bug_id"],"verify_patches"))
    # repairllama_main.py is always from root directory (not build-system specific)
    shutil.copy2(join(script_dir, "repairllama_main.py"),join(project["subject"],project["bug_id"],"repairllama_main.py"))
    
    # Get Java version from metadata
    java_version = project.get('java_version', 8)  # Default to Java 8 if not specified

    # Update install_deps with correct Java version
    # For Maven templates: replace openjdk-8-jdk pattern
    # For Gradle/Ant templates: replace <JAVA_VERSION> placeholder
    os.system("sed -i 's/openjdk-[0-9]*-jdk/openjdk-{}-jdk/' {}".format(java_version, join(project["subject"],project["bug_id"],"install_deps")))
    os.system("sed -i 's/<JAVA_VERSION>/{}/' {}".format(java_version, join(project["subject"],project["bug_id"],"install_deps")))
    
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
        os.system("sed -i '0,/<SUB_PROJECT>/s/<SUB_PROJECT>/{}/' {}".format(escaped_x, join(project["subject"],project["bug_id"],"verify_patches")))

    else:
        # Empty project_name means build entire project (keep <SUB_PROJECT> placeholder)
        print(f"Empty project_name for {project['id']} - will build entire project")
